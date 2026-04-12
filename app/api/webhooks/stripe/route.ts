import { NextResponse } from 'next/server';
import Stripe from 'stripe';
import { Pool } from '@neondatabase/serverless';

// Validate required environment variables at startup
function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} environment variable is not set`);
  return value;
}

const stripeSecretKey = requireEnv('STRIPE_SECRET_KEY');
const stripeWebhookSecret = requireEnv('STRIPE_WEBHOOK_SECRET');
const databaseUrl = requireEnv('DATABASE_URL');

// Initialize Stripe
const stripe = new Stripe(stripeSecretKey, {
  apiVersion: '2023-10-16',
});

// Initialize Neon DB Pool (Target: frosty-dew-64828454)
const pool = new Pool({ connectionString: databaseUrl });

export async function POST(req: Request) {
  const body = await req.text();
  const signature = req.headers.get('stripe-signature') as string;

  let event: Stripe.Event;

  // 🛡️ SECURITY: SIGNATURE VERIFICATION
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      stripeWebhookSecret
    );
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error(`⚠️ Webhook signature verification failed: ${message}`);
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  // Handle the event
  if (event.type === 'payment_intent.succeeded') {
    const paymentIntent = event.data.object as Stripe.PaymentIntent;

    const referenceId = paymentIntent.id;
    const amountUsd = paymentIntent.amount / 100; // Convert cents to dollars
    const allocatedTithe = amountUsd * 0.10; // 10% tithe allocation

    // 🏛️ INTEGRITY: IDEMPOTENCY & SCHEMA MAPPING
    const query = `
      INSERT INTO transactions (reference_id, amount_usd, allocated_tithe)
      VALUES ($1, $2, $3)
      ON CONFLICT (reference_id)
      DO UPDATE SET
        amount_usd = EXCLUDED.amount_usd,
        allocated_tithe = EXCLUDED.allocated_tithe;
    `;

    try {
      await pool.query(query, [referenceId, amountUsd, allocatedTithe]);
      console.log(`💎 Ledger Updated: ${referenceId} | $${amountUsd}`);
    } catch (dbError) {
      console.error('Transaction recording failed:', dbError);
      return NextResponse.json({ error: 'Database error' }, { status: 500 });
    }
  }

  return NextResponse.json({ received: true }, { status: 200 });
}
