"""
Database connection and initialization for MySQL
"""
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ai_image_detection')
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Initialize database tables"""
    try:
        # First connect without specifying database to create it if needed
        temp_config = DB_CONFIG.copy()
        db_name = temp_config.pop('database')
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        print(f"✅ Database '{db_name}' ready")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created/verified users table")
        
        # Create user_manual table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_manual (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                file_path VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created/verified user_manual table")
        
        # Create scam_tips table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scam_tips (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                image_path VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created/verified scam_tips table")
        
        # Create malaysia_cases table (scam-cases)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS malaysia_cases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                headline VARCHAR(255) NOT NULL,
                image_path VARCHAR(500),
                news_link VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created/verified malaysia_cases table")
        
        # Create ai_detections table (for storing AI detection results)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_detections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                image_path VARCHAR(500) NOT NULL,
                is_ai_generated BOOLEAN NOT NULL,
                confidence_percent DECIMAL(5, 2) NOT NULL,
                probability_score DECIMAL(10, 4) NOT NULL,
                likely_generator VARCHAR(255),
                explanation TEXT,
                user_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        print("✅ Created/verified ai_detections table")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ All database tables initialized successfully")
        
    except Error as e:
        print(f"❌ Error initializing database: {e}")
        raise

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        fetch_one: Return single row
        fetch_all: Return all rows
        
    Returns:
        Query results or lastrowid for INSERT
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid
            
        cursor.close()
        connection.close()
        return result
        
    except Error as e:
        print(f"Database error: {e}")
        if connection:
            connection.close()
        return None
