import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_PARAMS = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "admin123", # From .env
}

TARGET_DB = "smartquote"

def check_db():
    print(f"1. Attempting to connect to '{TARGET_DB}'...")
    try:
        conn = psycopg2.connect(**DB_PARAMS, dbname=TARGET_DB)
        conn.close()
        print(f"SUCCESS: Connected to '{TARGET_DB}'.")
        return True
    except psycopg2.OperationalError as e:
        print(f"FAILURE: Could not connect to '{TARGET_DB}'.")
        print(f"Error: {e}")
    
    print(f"\n2. Attempting to connect to 'postgres' (default config) to check if '{TARGET_DB}' exists...")
    try:
        conn = psycopg2.connect(**DB_PARAMS, dbname="postgres")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TARGET_DB,))
        exists = cur.fetchone()
        
        if exists:
            print(f"INFO: Database '{TARGET_DB}' exists, but connection failed earlier. Check permissions or concurrent connections.")
        else:
            print(f"DIAGNOSIS: Database '{TARGET_DB}' does NOT exist.")
            print("SUGGESTION: You need to create the database.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"CRITICAL: Could not connect to 'postgres' database either.")
        print(f"Error: {e}")
        print("DIAGNOSIS: Database server might be down, or credentials in .env (password: admin123) are incorrect.")

if __name__ == "__main__":
    check_db()
