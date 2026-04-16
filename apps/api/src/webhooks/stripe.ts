// apps/api/src/webhooks/stripe.ts
//
// Triumvirate-Axion Stripe webhook handler.
//
// Fixes vs. prior version:
//   1. Real idempotency via processed_stripe_events table on event.id,
//      not ON CONFLICT DO UPDATE (which was last-write-wins).
//   2. Removed INSERTs into generated columns (schema was generating them
//      AND the handler was inserting them; Postgres would have rejected).
//      Migration now has plain columns, handler computes and inserts all.
//   3. ON CONFLICT (reference_id) DO NOTHING on the ledger — the event-id
//      dedup is the source of truth; the UNIQUE on reference_id is a
//      secondary guard.
//   4. Skeletons for charge.refunded, charge.dispute.created,
//      payment_intent.succeeded, invoice.payment_succeeded so the 5-event
//      integration test has hooks to exercise. Fill these in per business
//      rules (refund handling, subscription ledger semantics, etc.).
//   5. Switched to Stripe's expand: ['balance_transaction'] on retrieval
//      path where applicable, so we don't double-round-trip per webhook.
//   6. Currency preserved instead of assumed-USD.

import Stripe from 'stripe';
import { neon } from '@neondatabase/serverless';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  // Pin to your Stripe account's current API version. Bump deliberately.
  apiVersion: '2025-03-31.basil' as Stripe.LatestApiVersion,
});

const sql = neon(process.env.DATABASE_URL!);

// Tithe rate is config, not code. Move to env or a config table before
// multi-tenant. Hardcoded here to match current Axion spec.
const TITHE_RATE_BPS = 1500; // 15.00% expressed in basis points (integer math)

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Integer-safe tithe: (net * 1500) / 10000, floored. */
function computeTithe(netMinor: number): number {
  return Math.floor((netMinor * TITHE_RATE_BPS) / 10000);
}

/** Returns the fee in the charge's currency, or 0 if unresolvable. */
function extractFee(charge: Stripe.Charge): number {
  const bt = charge.balance_transaction;
  if (!bt || typeof bt === 'string') return 0; // not expanded — caller should expand
  // NOTE: bt.fee is in bt.currency. If bt.currency !== charge.currency we have
  // an FX conversion scenario and this number is misleading. Flagging rather
  // than silently using it.
  if (bt.currency !== charge.currency) {
    console.warn(
      `⚠️ Fee currency (${bt.currency}) != charge currency (${charge.currency}) ` +
      `for charge ${charge.id}. Storing 0; reconcile via nightly job.`
    );
    return 0;
  }
  return bt.fee;
}

/**
 * Claims an event.id for processing. Returns true if this handler instance
 * should process it, false if another instance (or a retry) already has.
 */
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
  // TODO(business rule): decide whether refunds produce:
  //   (a) a status update on the original row,
  //   (b) an offsetting negative row (double-entry),
  //   (c) both.
  // Current implementation: status update only. Tithe is NOT clawed back
  // automatically — that's a treasury decision.
  const status =
    charge.amount_refunded === charge.amount ? 'refunded' : 'partially_refunded';
  await sql`
    UPDATE transactions
    SET status = ${status}
    WHERE reference_id = ${charge.id}
  `;
  console.log(`↩️  Ledger refund noted: ${charge.id} -> ${status}`);
}

async function handleChargeDisputeCreated(
  dispute: Stripe.Dispute
): Promise<void> {
  const chargeId =
    typeof dispute.charge === 'string' ? dispute.charge : dispute.charge.id;
  await sql`
    UPDATE transactions SET status = 'disputed'
    WHERE reference_id = ${chargeId}
  `;
  console.log(`⚖️  Ledger dispute flagged: ${chargeId}`);
}

async function handlePaymentIntentSucceeded(
  _pi: Stripe.PaymentIntent
): Promise<void> {
  // The charge.succeeded event already writes the ledger row. For PI-based
  // flows, we typically treat PI.succeeded as informational unless you need
  // to record intent-level metadata (customer_id, subscription_id) that
  // isn't on the charge. Leaving as no-op so we don't double-write.
}

async function handleInvoicePaymentSucceeded(
  _invoice: Stripe.Invoice
): Promise<void> {
  // TODO: for subscription ledger entries, link the invoice's charge to
  // the subscription_id and customer_id. Relevant to the Logos Agency
  // subscription dashboard — that dashboard will want subscription_id
  // on the ledger row, which this handler is the right place to backfill.
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
    console.error(`⚠️ Webhook signature verification failed: ${msg}`);
    return new Response(`Webhook Error: ${msg}`, { status: 400 });
  }

  // True idempotency: claim the event.id before doing any work.
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
        // Re-retrieve with balance_transaction expanded so extractFee() works
        // without a second round-trip pattern. This is ONE Stripe call, same
        // as the prior version, but it returns a fully-populated charge.
        if (charge.balance_transaction && typeof charge.balance_transaction === 'string') {
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
        await handlePaymentIntentSucceeded(
          event.data.object as Stripe.PaymentIntent
        );
        break;
      case 'invoice.payment_succeeded':
        await handleInvoicePaymentSucceeded(event.data.object as Stripe.Invoice);
        break;
      default:
        // Not an error — Stripe sends many event types. Dedup row is already
        // written, so we won't re-see this one.
        console.log(`ℹ️  Unhandled event type: ${event.type}`);
    }

    return new Response(JSON.stringify({ received: true }), { status: 200 });
  } catch (err: unknown) {
    // IMPORTANT: if processing fails AFTER we claimed the event, the retry
    // from Stripe will be deduped and silently skipped. For a financial
    // ledger this is the wrong default. Roll back the claim so Stripe can
    // retry.
    await sql`DELETE FROM processed_stripe_events WHERE event_id = ${event.id}`;
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`🔥 Handler error for ${event.id} (${event.type}): ${msg}`);
    return new Response(`Handler Error: ${msg}`, { status: 500 });
  }
}
