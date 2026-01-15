import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='hospital_management',
            user='root',              # Your MySQL username
            password='root123'    # ⚠️ CHANGE THIS to your MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def close_connection(connection):
    """Close database connection"""
    if connection and connection.is_connected():
        connection.close()