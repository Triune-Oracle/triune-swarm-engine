// app/api/webhooks/stripe/route.ts
// Next.js App Router — Triumvirate-Axion Stripe webhook handler.
//
// Hardened vs. prior version:
//   1. Real idempotency: claim event.id in processed_stripe_events before
//      any work. ON CONFLICT DO NOTHING is a secondary guard only.
//   2. Schema fix: no GENERATED ALWAYS columns. All values computed here.
//   3. Integer tithe math: (net * 1500) / 10000, no float rounding.
//   4. FX fee guard: fee stored as 0 and flagged if bt.currency != charge.currency.
//   5. Retry-safe: rolls back the event claim on handler error so Stripe
//      can retry rather than being silently deduped.
//   6. 5-event coverage: charge.succeeded, charge.refunded,
//      charge.dispute.created, payment_intent.succeeded (no-op),
//      invoice.payment_succeeded (stub — see TODO).
//
// Required: run migrations/001_ledger_core.sql before deploying.

import Stripe from 'stripe';
import { neon } from '@neondatabase/serverless';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  // Pin to your Stripe account's current API version. Bump deliberately.
  apiVersion: '2025-03-31.basil' as Stripe.LatestApiVersion,
});

const sql = neon(process.env.DATABASE_URL!);

// Tithe rate in basis points. 1500 bps = 15.00%.
// Move to env or a config table before multi-tenant.
const TITHE_RATE_BPS = 1500;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function computeTithe(netMinor: number): number {
  return Math.floor((netMinor * TITHE_RATE_BPS) / 10000);
}

function extractFee(charge: Stripe.Charge): number {
  const bt = charge.balance_transaction;
  if (!bt || typeof bt === 'string') return 0;
  if (bt.currency !== charge.currency) {
    console.warn(
      `⚠️ Fee currency (${bt.currency}) != charge currency (${charge.currency}) ` +
      `for charge ${charge.id}. Storing fee=0; reconcile via nightly job.`
    );
    return 0;
  }
  return bt.fee;
}

async function claimEvent(event: Stripe.Event): Promise<boolean> {
  const rows = await sql`
    INSERT INTO processed_stripe_events (event_id, event_type)
    VALUES (${event.id}, ${event.type})
    ON CONFLICT (event_id) DO NOTHING
    RETURNING event_id
  `;
  return rows.length > 0;
}

// ---------------------------------------------------------------------------
// Per-event handlers
// ---------------------------------------------------------------------------

async function handleChargeSucceeded(charge: Stripe.Charge): Promise<void> {
  const amount = charge.amount;
  const fee = extractFee(charge);
  const net = amount - fee;
  const allocatedTithe = computeTithe(net);

  await sql`
    INSERT INTO transactions (
      reference_id, stripe_charge_id,
      amount, fee, net, allocated_tithe,
      currency, status
    ) VALUES (
      ${charge.id}, ${charge.id},
      ${amount}, ${fee}, ${net}, ${allocatedTithe},
      ${charge.currency}, 'succeeded'
    )
    ON CONFLICT (reference_id) DO NOTHING
  `;

  console.log(
    `✅ Ledger anchored: ${charge.id} | ${charge.currency} ` +
    `net=${net} tithe=${allocatedTithe}`
  );
}

async function handleChargeRefunded(charge: Stripe.Charge): Promise<void> {
  // TODO(business rule): status update only for now. Tithe clawback is a
  // treasury decision — options are (a) no clawback [current], (b) offsetting
  // double-entry row, (c) update in place. Waiting on owner decision.
  const status =
    charge.amount_refunded === charge.amount ? 'refunded' : 'partially_refunded';
  await sql`
    UPDATE transactions SET status = ${status}
    WHERE reference_id = ${charge.id}
  `;
  console.log(`↩️  Refund noted: ${charge.id} → ${status}`);
}

async function handleChargeDisputeCreated(dispute: Stripe.Dispute): Promise<void> {
  const chargeId =
    typeof dispute.charge === 'string' ? dispute.charge : dispute.charge.id;
  await sql`
    UPDATE transactions SET status = 'disputed'
    WHERE reference_id = ${chargeId}
  `;
  console.log(`⚖️  Dispute flagged: ${chargeId}`);
}

async function handlePaymentIntentSucceeded(_pi: Stripe.PaymentIntent): Promise<void> {
  // charge.succeeded is the canonical ledger event for PI-based flows.
  // No-op here to avoid double-writing.
}

async function handleInvoicePaymentSucceeded(_invoice: Stripe.Invoice): Promise<void> {
  // TODO: wire subscription_id + customer_id onto the ledger row for the
  // Logos Agency subscription dashboard. Blocked on owner decision:
  // is Triumvirate-Axion charging one-offs or subscriptions?
}

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

export async function POST(request: Request): Promise<Response> {
  const payload = await request.text();
  const signature = request.headers.get('stripe-signature');

  if (!signature) {
    return new Response('Missing stripe-signature', { status: 400 });
  }

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      payload,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`⚠️ Signature verification failed: ${msg}`);
    return new Response(`Webhook Error: ${msg}`, { status: 400 });
  }

  // Claim event.id before any work. If already claimed, this is a Stripe
  // retry of an event we already processed — skip cleanly.
  const claimed = await claimEvent(event);
  if (!claimed) {
    console.log(`⏭  Event ${event.id} already processed — skipping.`);
    return new Response(JSON.stringify({ received: true, deduped: true }), {
      status: 200,
    });
  }

  try {
    switch (event.type) {
      case 'charge.succeeded': {
        let charge = event.data.object as Stripe.Charge;
        if (typeof charge.balance_transaction === 'string') {
          charge = await stripe.charges.retrieve(charge.id, {
            expand: ['balance_transaction'],
          });
        }
        await handleChargeSucceeded(charge);
        break;
      }
      case 'charge.refunded':
        await handleChargeRefunded(event.data.object as Stripe.Charge);
        break;
      case 'charge.dispute.created':
        await handleChargeDisputeCreated(event.data.object as Stripe.Dispute);
        break;
      case 'payment_intent.succeeded':
        await handlePaymentIntentSucceeded(event.data.object as Stripe.PaymentIntent);
        break;
      case 'invoice.payment_succeeded':
        await handleInvoicePaymentSucceeded(event.data.object as Stripe.Invoice);
        break;
      default:
        console.log(`ℹ️  Unhandled event type: ${event.type}`);
    }

    return new Response(JSON.stringify({ received: true }), { status: 200 });
  } catch (err: unknown) {
    // Roll back the claim so Stripe can retry. Without this, a failed handler
    // would silently skip the event on retry — wrong for a financial ledger.
    await sql`DELETE FROM processed_stripe_events WHERE event_id = ${event.id}`;
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`🔥 Handler error for ${event.id} (${event.type}): ${msg}`);
    return new Response(`Handler Error: ${msg}`, { status: 500 });
  }
}
