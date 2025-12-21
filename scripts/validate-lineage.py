import sqlite3
import os
import sys

LINEAGE_DB_PATH = os.path.join(".shadowscrolls", "lineage", "mirror_lineage.db")

def validate_lineage_db():
    """Validates the existence and basic schema of the lineage database."""
    print(f"--- Validating Lineage DB: {LINEAGE_DB_PATH} ---")

    os.makedirs(os.path.dirname(LINEAGE_DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(LINEAGE_DB_PATH)
    cursor = conn.cursor()
    
    # Ensure the table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lineage_events (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            source_repo TEXT NOT NULL,
            commit_hash TEXT,
            details_json TEXT
        )
    """)
    conn.commit()
    print("✅ Ensured 'lineage_events' table exists.")

    try:
        conn = sqlite3.connect(LINEAGE_DB_PATH)
        cursor = conn.cursor()

        # 1. Check if the table exists (already ensured above, but keeping for logic flow)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lineage_events'")
        if cursor.fetchone() is None:
            print("❌ Table 'lineage_events' not found (This should not happen).")
            return False
        print("✅ Table 'lineage_events' confirmed to exist.")

        # 2. Check basic readability
        cursor.execute("SELECT COUNT(*) FROM lineage_events")
        count = cursor.fetchone()[0]
        print(f"✅ Database is readable. Found {count} records.")

        # 3. Check schema (simplified check for column count)
        cursor.execute("PRAGMA table_info(lineage_events)")
        columns = [col[1] for col in cursor.fetchall()]
        expected_columns = ['id', 'timestamp', 'event_type', 'source_repo', 'commit_hash', 'details_json']
        
        if all(col in columns for col in expected_columns):
            print(f"✅ Schema check passed. Found expected columns: {', '.join(expected_columns)}")
        else:
            print(f"❌ Schema check failed. Expected columns: {expected_columns}, Found: {columns}")
            return False

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ SQLite error during validation: {e}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if validate_lineage_db():
        print("\nLineage DB validation successful.")
        sys.exit(0)
    else:
        print("\nLineage DB validation failed.")
        sys.exit(1)
