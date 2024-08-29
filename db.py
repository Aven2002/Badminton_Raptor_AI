# db.py
import mysql.connector
from config import Config

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.DATABASE_HOST,
            user=Config.DATABASE_USER,
            password=Config.DATABASE_PASSWORD,
            database=Config.DATABASE_NAME
        )
        if connection.is_connected():
            print("MySQL connected...")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
