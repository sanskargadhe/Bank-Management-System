import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def connect_to_database():
    try:
        # pass
        connection = psycopg2.connect(
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT"),
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD")
        )
        print("Connected to PostgreSQL")
        return connection
    except Exception as error:
        print("Error Connecting to PostgreSQL database",error)
        return None
    
if __name__ == "__main__":
    conn = connect_to_database()
    if conn:
        conn.close()
        print("Connection Closed")