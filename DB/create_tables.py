import sqlite3
import os
import logging
from pathlib import Path

def create_tables(db_path):
    """Create missing tables in the database."""
    try:
        # Ensure the database file exists
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create student table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            gender TEXT,
            date_of_birth TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create enrollment table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            enrollment_date TEXT,
            completion_date TEXT,
            grade REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student(student_id),
            UNIQUE(student_id, course_id)
        )
        ''')
        
        # Create activity_log table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            action_type TEXT,
            action_description TEXT,
            entity_type TEXT,
            entity_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        conn.commit()
        logging.info("Successfully created missing tables")
        return True
    except Exception as e:
        logging.error(f"Error creating tables: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Get the database path from the environment or use a default
    db_path = os.getenv('DB_PATH', str(Path(__file__).parent / 'student_management.db'))
    create_tables(db_path)
