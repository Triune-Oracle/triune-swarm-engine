import os
import sqlite3
import sys

LINEAGE_DB_PATH = os.path.join(".shadowscrolls", "lineage", "mirror_lineage.db")

EXPECTED_TABLE_COLUMNS = {
    "sessions": [
        "id",
        "start_time",
        "end_time",
        "status",
        "execution_type",
        "metadata_json",
        "verification_hash",
        "created_at",
    ],
    "phases": [
        "id",
        "session_id",
        "phase_name",
        "start_time",
        "end_time",
        "status",
        "data_json",
        "data_hash",
        "error_message",
        "created_at",
    ],
    "events": [
        "id",
        "session_id",
        "phase_id",
        "event_type",
        "timestamp",
        "message",
        "data_json",
        "severity",
        "created_at",
    ],
    "verification_chain": [
        "id",
        "session_id",
        "previous_hash",
        "current_hash",
        "chain_position",
        "verification_data",
        "timestamp",
    ],
    "seen_events": [
        "event_key",
        "first_seen_at",
    ],
}

EXPECTED_INDEXES = [
    "idx_phases_session_id",
    "idx_events_session_id",
    "idx_events_phase_id",
    "idx_verification_chain_session_position",
]


def validate_lineage_db():
    """Validate lineage database schema against runtime expectations."""
    print(f"--- Validating Lineage DB: {LINEAGE_DB_PATH} ---")

    if not os.path.exists(LINEAGE_DB_PATH):
        print("❌ Lineage database file not found.")
        return False

    try:
        conn = sqlite3.connect(LINEAGE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0].lower()
        if journal_mode != "wal":
            print(f"❌ Expected WAL journal mode, found '{journal_mode}'.")
            return False
        print("✅ WAL mode enabled.")

        for table_name, expected_columns in EXPECTED_TABLE_COLUMNS.items():
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            )
            if cursor.fetchone() is None:
                print(f"❌ Missing table: {table_name}")
                return False

            cursor.execute(f"PRAGMA table_info({table_name})")
            actual_columns = [row[1] for row in cursor.fetchall()]
            missing = [column for column in expected_columns if column not in actual_columns]
            if missing:
                print(f"❌ Table {table_name} is missing columns: {missing}")
                return False
            print(f"✅ Table {table_name} schema OK.")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        actual_indexes = {row[0] for row in cursor.fetchall() if row[0]}
        for index_name in EXPECTED_INDEXES:
            if index_name not in actual_indexes:
                print(f"❌ Missing index: {index_name}")
                return False
        print("✅ Required indexes are present.")

        cursor.execute("SELECT COUNT(*) FROM sessions")
        print(f"✅ Database readable. Session rows: {cursor.fetchone()[0]}")

        conn.close()
        return True
    except sqlite3.Error as error:
        print(f"❌ SQLite error during validation: {error}")
        return False
    except Exception as error:
        print(f"❌ An unexpected error occurred: {error}")
        return False

if __name__ == "__main__":
    if validate_lineage_db():
        print("\nLineage DB validation successful.")
        sys.exit(0)
    else:
        print("\nLineage DB validation failed.")
        sys.exit(1)
