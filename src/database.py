import sqlite3
import json
import logging

DATABASE_FILE = "fact_checks.db"

def init_db():
    """Initializes the SQLite database and creates the fact_checks table."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fact_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim TEXT NOT NULL,
                claim_type TEXT,
                initial_response TEXT,
                assumptions TEXT,
                assumptions_verdicts TEXT,
                gathered_evidence TEXT,
                final_answer TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("PRAGMA table_info(fact_checks)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'claim_type' not in columns:
            cursor.execute("ALTER TABLE fact_checks ADD COLUMN claim_type TEXT")
            logging.info("Added 'claim_type' column to fact_checks table.")

        conn.commit()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def save_fact_check(fact_check_data: dict):
    """Saves a fact-check result to the database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fact_checks (claim, claim_type, initial_response, assumptions, assumptions_verdicts, gathered_evidence, final_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            fact_check_data.get('claim'),
            fact_check_data.get('claim_type'),
            fact_check_data.get('initial_response'),
            json.dumps(fact_check_data.get('assumptions')),
            json.dumps(fact_check_data.get('assumptions_verdicts')),
            json.dumps(fact_check_data.get('gathered_evidence')),
            fact_check_data.get('final_answer')
        ))
        conn.commit()
        logging.info(f"Fact-check for claim '{fact_check_data.get('claim')}' saved to database.")
    except sqlite3.Error as e:
        logging.error(f"Error saving fact-check to database: {e}")
    finally:
        if conn:
            conn.close()

def load_all_fact_checks() -> list:
    """Loads all fact-check results from the database."""
    conn = None
    fact_checks = []
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fact_checks ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        logging.info(f"Raw rows loaded from DB: {rows}") # Added logging
        for row in rows:
            fact_checks.append({
                'id': row[0],
                'claim': row[1],
                'claim_type': row[2],
                'initial_response': row[3],
                'assumptions': json.loads(row[4]) if row[4] else [],
                'assumptions_verdicts': json.loads(row[5]) if row[5] else [],
                'gathered_evidence': json.loads(row[6]) if row[6] else [],
                'final_answer': row[7],
                'timestamp': row[8]
            })
        logging.info(f"Loaded {len(fact_checks)} fact-checks from database.")
    except sqlite3.Error as e:
        logging.error(f"Error loading fact-checks from database: {e}")
    except json.JSONDecodeError as e: # Added JSON decode error handling
        logging.error(f"JSON decoding error in load_all_fact_checks: {e}. This might be due to old data format.")
        logging.error("Consider deleting fact_checks.db and rerunning if this persists.")
    finally:
        if conn:
            conn.close()
    return fact_checks