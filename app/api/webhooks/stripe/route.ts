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

const WAR_CHEST_TITHE_PERCENTAGE = 0.15; // 15% of each charge goes to the war chest

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

  // 📋 EVENT LOGGING
  console.log('stripe event:', { id: event.id, type: event.type });

  // Handle the event
  if (event.type === 'charge.succeeded') {
    const charge = event.data.object as Stripe.Charge;

    const referenceId = charge.id;
    const amountReceived = charge.amount; // in cents
    const warChestTithe = Math.round(amountReceived * WAR_CHEST_TITHE_PERCENTAGE); // war chest tithe, in cents

    // 🏛️ INTEGRITY: IDEMPOTENCY & SCHEMA MAPPING
    const query = `
      INSERT INTO revenue_log (reference_id, amount_received, war_chest_tithe)
      VALUES ($1, $2, $3)
      ON CONFLICT (reference_id)
      DO UPDATE SET
        amount_received = EXCLUDED.amount_received,
        war_chest_tithe = EXCLUDED.war_chest_tithe;
    `;

    try {
      await pool.query(query, [referenceId, amountReceived, warChestTithe]);
      console.log(`💎 Revenue Logged: ${referenceId} | ${amountReceived}¢ received | ${warChestTithe}¢ to war chest`);
    } catch (dbError) {
      console.error('Revenue log insert failed:', dbError);
      return NextResponse.json({ error: 'Database error' }, { status: 500 });
    }
  }

  return NextResponse.json({ received: true }, { status: 200 });
}
