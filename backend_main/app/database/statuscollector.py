# database/sync_status.py
from pymongo import MongoClient
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import psycopg2

def sync_machine_status():
    load_dotenv()

    # MongoDB setup
    mongo_uri = os.getenv("MONGO_URI")
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client["MTLINKi"]
    mongo_collection = mongo_db["L1_Pool_Opened"]

    # PostgreSQL setup
    pg_conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)

    print(" Connected to MongoDB and PostgreSQL")

    # Ensure table exists
    pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS machine_status_log (
        id SERIAL PRIMARY KEY,
        machine_name TEXT NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        value TEXT NOT NULL
    )
    """)
    pg_conn.commit()
    print("🛠️  Ensured machine_status_log table exists.")

    docs = mongo_collection.find()
    status_snapshot = []

    print("🔍 Checking documents in MongoDB...")

    for doc in docs:
        machine = doc.get("L1Name")
        updated_at = doc.get("updatedate")
        value = doc.get("value")

        if not (machine and updated_at and value):
            print(f"⚠️  Skipped invalid document: {doc}")
            continue

        pg_cursor.execute("""
            SELECT value FROM machine_status_log
            WHERE machine_name = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """, (machine,))
        latest = pg_cursor.fetchone()

        if latest is None or latest["value"] != value:
            pg_cursor.execute("""
                INSERT INTO machine_status_log (machine_name, updated_at, value)
                VALUES (%s, %s, %s)
            """, (machine, updated_at, value))
            print(f"✔ Inserted: {machine} | {updated_at} | {value}")
        else:
            print(f"Skipped: {machine} (no value change: {value})")


        status_snapshot.append({
            "machine_name": machine,
            "updated_at": str(updated_at),
            "value": value
        })

    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

    with open("latest_machine_status.json", "w") as f:
        json.dump(status_snapshot, f, indent=4)

    print("💾 Snapshot saved to latest_machine_status.json")
    print("✅ Data sync complete.")
