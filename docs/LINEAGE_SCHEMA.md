# .shadowscrolls Lineage Database Schema

This document formalizes the runtime schema for `mirror_lineage.db` in `.shadowscrolls/lineage/`.

## SQLite runtime settings

- `PRAGMA journal_mode = WAL`
- `PRAGMA busy_timeout = 5000` (override with `LINEAGE_SQLITE_BUSY_TIMEOUT_MS`)

## Tables

### `sessions`
- `id` TEXT PRIMARY KEY
- `start_time` TEXT NOT NULL
- `end_time` TEXT
- `status` TEXT NOT NULL DEFAULT `'active'`
- `execution_type` TEXT
- `metadata_json` TEXT
- `verification_hash` TEXT
- `created_at` TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP

### `phases`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `session_id` TEXT NOT NULL REFERENCES `sessions(id)`
- `phase_name` TEXT NOT NULL
- `start_time` TEXT NOT NULL
- `end_time` TEXT
- `status` TEXT NOT NULL DEFAULT `'active'`
- `data_json` TEXT
- `data_hash` TEXT
- `error_message` TEXT
- `created_at` TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP

### `events`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `session_id` TEXT NOT NULL REFERENCES `sessions(id)`
- `phase_id` INTEGER REFERENCES `phases(id)`
- `event_type` TEXT NOT NULL
- `timestamp` TEXT NOT NULL
- `message` TEXT
- `data_json` TEXT
- `severity` TEXT NOT NULL DEFAULT `'info'`
- `created_at` TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP

### `verification_chain`
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `session_id` TEXT NOT NULL REFERENCES `sessions(id)`
- `previous_hash` TEXT
- `current_hash` TEXT NOT NULL
- `chain_position` INTEGER NOT NULL
- `verification_data` TEXT
- `timestamp` TEXT NOT NULL

### `seen_events`
- `event_key` TEXT PRIMARY KEY
- `first_seen_at` TEXT NOT NULL

## Indexes

- `idx_phases_session_id` on `phases(session_id)`
- `idx_events_session_id` on `events(session_id)`
- `idx_events_phase_id` on `events(phase_id)`
- `idx_verification_chain_session_position` on `verification_chain(session_id, chain_position)`

## Validation Script (`scripts/validate-lineage.py`)

The validator checks:
1. Database file existence and readability.
2. WAL journal mode.
3. Expected tables and columns listed above.
4. Required indexes listed above.
