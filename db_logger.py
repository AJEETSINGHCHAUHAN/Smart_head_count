from db_config import get_connection
from datetime import datetime

def insert_count_to_db(count):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO people_log (count, timestamp) VALUES (%s, %s)"
        cursor.execute(query, (count, datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error inserting count into database: {e}")
