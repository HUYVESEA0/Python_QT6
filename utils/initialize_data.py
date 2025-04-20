import logging
from DB.db_manager import DatabaseManager
from datetime import datetime

def initialize_activity_data(db_manager):
    """
    Initialize activity data with proper keys to prevent 'No item with that key' errors.
    """
    try:
        # Make sure required tables exist
        db_manager.ensure_tables_exist()
        
        # Check if activity table already has data
        check_query = "SELECT COUNT(*) FROM activity_log"
        result = db_manager.execute_query(check_query)
        count = result[0][0] if result else 0
        
        if count > 0:
            logging.info("Activity log table already has data. Skipping initialization.")
            return True
        
        # Define activity data with all required fields - matching database column names
        activities = [
            {
                "action_type": "SYSTEM",
                "action_description": "System initialized", 
                "entity_type": "SYSTEM",
                "entity_id": "0",
                "user_id": 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "action_type": "LOGIN",
                "action_description": "Administrator first login",
                "entity_type": "USER",
                "entity_id": "1",
                "user_id": 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        # Insert activity data
        for activity in activities:
            query = """
            INSERT INTO activity_log (action_type, action_description, entity_type, entity_id, user_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                activity["action_type"],
                activity["action_description"],
                activity["entity_type"],
                activity["entity_id"],
                activity["user_id"],
                activity["timestamp"]
            )
            db_manager.execute_insert(query, params)
            
        logging.info("Successfully initialized activity data")
        return True
        
    except Exception as e:
        logging.error(f"Error initializing activity data: {e}")
        return False

def initialize_all_data(db_path):
    """Initialize all application data"""
    try:
        db_manager = DatabaseManager(db_path)
        initialize_activity_data(db_manager)
        return True
    except Exception as e:
        logging.error(f"Error in data initialization: {str(e)}")
        return False
    finally:
        if 'db_manager' in locals() and db_manager:
            db_manager.close()
