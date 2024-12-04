import sqlite3

def get_db_connection():
    conn = sqlite3.connect('standupbot.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Function to Insert/Update/Delete
def execute_query(query, params=None):
    if params is None:
        params = ()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"DatabaseError: {e}")
    finally:
        conn.close()

# Function to fetch one record from the database
def fetch_one(query, params=None):
    if params is None:
        params = ()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    except sqlite3.DatabaseError as e:
        print(f"DatabaseError: {e}")
    finally:
        conn.close()

# Function to fetch multiple records from the database
def fetch_all(query, params=None):
    if params is None:
        params = ()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    except sqlite3.DatabaseError as e:
        print(f"DatabaseError: {e}")
    finally:
        conn.close()