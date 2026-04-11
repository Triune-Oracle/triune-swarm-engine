import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { neon } from "@neondatabase/serverless";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2023-10-16",
});

const sql = neon(process.env.DATABASE_URL!);

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get("stripe-signature");

  if (!signature) {
    return NextResponse.json(
      { error: "Missing stripe-signature header" },
      { status: 400 }
    );
  }

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    console.error(`Webhook signature verification failed: ${message}`);
    return NextResponse.json(
      { error: `Webhook signature verification failed: ${message}` },
      { status: 400 }
    );
  }

  if (event.type === "payment_intent.succeeded") {
    const paymentIntent = event.data.object as Stripe.PaymentIntent;
    const referenceId = paymentIntent.id;
    const amountUsd = paymentIntent.amount / 100;
    const allocatedTithe = amountUsd * 0.1;

    try {
      await sql`
        INSERT INTO transactions (reference_id, amount_usd, allocated_tithe)
        VALUES (${referenceId}, ${amountUsd}, ${allocatedTithe})
        ON CONFLICT (reference_id) DO UPDATE SET
          amount_usd = EXCLUDED.amount_usd,
          allocated_tithe = EXCLUDED.allocated_tithe;
      `;

      console.log(
        `Transaction recorded: ${referenceId} | $${amountUsd.toFixed(2)} | tithe: $${allocatedTithe.toFixed(2)}`
      );
    } catch (dbError) {
      console.error("Database insert failed:", dbError);
      return NextResponse.json(
        { error: "Database insert failed" },
        { status: 500 }
      );
    }
  }

  return NextResponse.json({ received: true }, { status: 200 });
}
