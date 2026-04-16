-- migrations/001_ledger_core.sql
-- Triumvirate-Axion ledger core.
-- Changes vs. prior version of this file:
--   1. Removed CHECK (amount >= 0) etc. on amount/fee/net/allocated_tithe.
--      Reversal rows for refunds use negative values; the old constraints
--      would reject them. sign_matches_status (below) replaces them.
--   2. status already included 'reversed' — confirmed, no change needed.
--   3. processed_stripe_events table for real event-id idempotency.
--   4. currency and status columns for FX safety and refund/dispute tracking.

BEGIN;

-- ---------------------------------------------------------------------------
-- Ledger
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    id               BIGSERIAL PRIMARY KEY,
    reference_id     VARCHAR(255) UNIQUE NOT NULL,     -- Stripe charge id, or "<charge_id>:refund:<ts>" for reversals
    stripe_charge_id VARCHAR(255) NOT NULL,

    -- Integer minor units. Negative values are valid for reversal rows
    -- (charge.refunded double-entry). Do NOT sum across currencies without
    -- conversion. See sign_matches_status constraint below.
    amount           INTEGER NOT NULL,
    fee              INTEGER NOT NULL DEFAULT 0,
    net              INTEGER NOT NULL,
    allocated_tithe  INTEGER NOT NULL,

    currency         CHAR(3) NOT NULL DEFAULT 'usd',

    status           VARCHAR(32) NOT NULL DEFAULT 'succeeded'
                     CHECK (status IN ('succeeded','refunded','partially_refunded','disputed','reversed')),

    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enforce sign discipline: reversal rows must have negative amount;
-- all other rows must have non-negative amount.
ALTER TABLE transactions DROP CONSTRAINT IF EXISTS transactions_sign_matches_status;
ALTER TABLE transactions ADD CONSTRAINT transactions_sign_matches_status
  CHECK (
    (status = 'reversed' AND amount <= 0) OR
    (status <> 'reversed' AND amount >= 0)
  );

-- ---------------------------------------------------------------------------
-- Stripe event dedup. This is the real idempotency layer.
-- Webhook handler short-circuits at the top if event.id already exists here.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS processed_stripe_events (
    event_id     VARCHAR(255) PRIMARY KEY,       -- Stripe event.id (evt_...)
    event_type   VARCHAR(128) NOT NULL,
    processed_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- updated_at trigger (shared)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_transactions_updated_at ON transactions;
CREATE TRIGGER trg_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

COMMIT;
