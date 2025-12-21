# .shadowscrolls Lineage Database Schema

This document formalizes the schema for the `mirror_lineage.db` SQLite database located in the `.shadowscrolls/lineage/` directory.

## Table: `lineage_events`

Tracks all significant events related to the Mirror Watcher automation.

| Column Name | Data Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | Primary key, auto-incrementing. | PRIMARY KEY, NOT NULL |
| `timestamp` | TEXT | UTC timestamp of the event. | NOT NULL |
| `event_type` | TEXT | Type of event (e.g., `REPO_SYNC`, `ANALYSIS_START`, `DEPLOYMENT_SUCCESS`). | NOT NULL |
| `source_repo` | TEXT | The repository the event originated from. | NOT NULL |
| `commit_hash` | TEXT | The commit hash associated with the event. | |
| `details_json` | TEXT | JSON string containing event-specific details (e.g., health score, deployment URL). | |

## Validation Script (`scripts/validate-lineage.py`)

A script should be implemented to:
1. Connect to `mirror_lineage.db`.
2. Verify the existence of the `lineage_events` table.
3. Check the column names and data types against this schema.
4. Run a simple query to ensure the database is readable.

## Reporting Process

New major integration changes or audit runs should append a new report to `.shadowscrolls/reports/` rather than overwriting existing ones. Reports should be named with a timestamp, e.g., `initial-setup-20251221.md`.
