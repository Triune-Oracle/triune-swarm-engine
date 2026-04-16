-- migrations/001_ledger_core.sql
-- Triumvirate-Axion ledger core.
-- Fixes vs. prior version:
--   1. Removed GENERATED ALWAYS STORED on net_usd and allocated_tithe.
--      Prior version collided with the webhook's explicit INSERT and would
--      have thrown: "cannot insert a non-DEFAULT value into generated column".
--   2. Removed the redundant idx_transactions_reference index (UNIQUE already
--      creates one).
--   3. Added processed_stripe_events table for true event-ID idempotency.
--   4. Added status column so refunds/disputes don't silently overwrite.
--   5. Added currency column — fees and amounts are NOT guaranteed to be USD.

BEGIN;

-- ---------------------------------------------------------------------------
-- Ledger
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    id               BIGSERIAL PRIMARY KEY,
    reference_id     VARCHAR(255) UNIQUE NOT NULL,     -- Stripe charge id (or PI id)
    stripe_charge_id VARCHAR(255) NOT NULL,

    -- Integer minor units only. Column is named amount_usd for continuity,
    -- but currency column below is authoritative. DO NOT mix currencies in
    -- aggregate queries without converting.
    amount           INTEGER NOT NULL CHECK (amount           >= 0),
    fee              INTEGER NOT NULL DEFAULT 0 CHECK (fee    >= 0),
    net              INTEGER NOT NULL CHECK (net              >= 0),
    allocated_tithe  INTEGER NOT NULL CHECK (allocated_tithe  >= 0),

    currency         CHAR(3) NOT NULL DEFAULT 'usd',

    status           VARCHAR(32) NOT NULL DEFAULT 'succeeded'
                     CHECK (status IN ('succeeded','refunded','partially_refunded','disputed','reversed')),

    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
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
