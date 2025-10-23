"""
Info Database Operations
Handles database operations for application settings, history, and system info
"""

import mysql.connector
from datetime import datetime


class InfoDatabase:
    """Database handler for info tab operations."""
    
    def __init__(self, host='localhost', user='root', password='root', database='welvision_db'):
        """
        Initialize database connection.
        
        Args:
            host: MySQL server host
            user: Database username
            password: Database password
            database: Database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Exception as e:
            print(f"❌ Error connecting to MySQL database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def get_app_title(self):
        """
        Get current application title from database.
        
        Returns:
            str: Application title or default "WELVISION"
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_by VARCHAR(100)
                )
            """)
            
            # Get title
            cursor.execute("SELECT setting_value FROM app_settings WHERE setting_key = 'app_title'")
            result = cursor.fetchone()
            
            cursor.close()
            
            if result:
                return result[0]
            else:
                return "WELVISION"
        
        except Exception as e:
            print(f"❌ Error getting app title: {e}")
            return "WELVISION"
    
    def update_app_title(self, new_title, updated_by):
        """
        Update application title in database.
        
        Args:
            new_title: New application title
            updated_by: User who updated the title
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_by VARCHAR(100)
                )
            """)
            
            # Update or insert title
            cursor.execute("""
                INSERT INTO app_settings (setting_key, setting_value, updated_by)
                VALUES ('app_title', %s, %s)
                ON DUPLICATE KEY UPDATE 
                    setting_value = VALUES(setting_value),
                    updated_by = VALUES(updated_by),
                    updated_at = CURRENT_TIMESTAMP
            """, (new_title, updated_by))
            
            self.connection.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            print(f"❌ Error updating app title: {e}")
            return False
    
    def get_settings_history(self, limit=100):
        """
        Get settings change history.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            list: List of history records
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Create history table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    change_type VARCHAR(100),
                    description TEXT,
                    changed_by VARCHAR(100),
                    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Get history
            cursor.execute("""
                SELECT change_type, description, changed_by, change_timestamp
                FROM settings_history
                ORDER BY change_timestamp DESC
                LIMIT %s
            """, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            
            return results
        
        except Exception as e:
            print(f"❌ Error getting settings history: {e}")
            return []
    
    def add_settings_history(self, change_type, description, changed_by):
        """
        Add entry to settings history.
        
        Args:
            change_type: Type of change (e.g., "App Title", "Database Config")
            description: Description of the change
            changed_by: User who made the change
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Create history table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    change_type VARCHAR(100),
                    description TEXT,
                    changed_by VARCHAR(100),
                    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert history record
            cursor.execute("""
                INSERT INTO settings_history (change_type, description, changed_by)
                VALUES (%s, %s, %s)
            """, (change_type, description, changed_by))
            
            self.connection.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            print(f"❌ Error adding settings history: {e}")
            return False
    
    def clear_settings_history(self):
        """
        Clear all settings history records.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM settings_history")
            self.connection.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            print(f"❌ Error clearing settings history: {e}")
            return False
    
    def get_threshold_history(self, filter_type='Overall', from_date=None, to_date=None):
        """
        Get threshold history from BF and/or OD threshold tables.
        
        Args:
            filter_type: 'BF', 'OD', or 'Overall'
            from_date: Start date for filtering
            to_date: End date for filtering
            
        Returns:
            list: List of threshold history records
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            results = []
            
            # Query BF history if needed
            if filter_type in ['BF', 'Overall']:
                query = """
                    SELECT id, 'BF' as type, model_name, employee_id, change_timestamp, 
                           defect_threshold, model_threshold
                    FROM bf_threshold_history
                    WHERE DATE(change_timestamp) BETWEEN %s AND %s
                    ORDER BY change_timestamp DESC
                """
                cursor.execute(query, (from_date, to_date))
                bf_results = cursor.fetchall()
                results.extend(bf_results)
            
            # Query OD history if needed
            if filter_type in ['OD', 'Overall']:
                query = """
                    SELECT id, 'OD' as type, model_name, employee_id, change_timestamp, 
                           defect_threshold, model_threshold
                    FROM od_threshold_history
                    WHERE DATE(change_timestamp) BETWEEN %s AND %s
                    ORDER BY change_timestamp DESC
                """
                cursor.execute(query, (from_date, to_date))
                od_results = cursor.fetchall()
                results.extend(od_results)
            
            cursor.close()
            
            # Sort by timestamp descending
            results.sort(key=lambda x: x[4], reverse=True)
            
            return results
        
        except Exception as e:
            print(f"❌ Error getting threshold history: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def clear_threshold_history(self, filter_type='Overall'):
        """
        Clear threshold history for specified type.
        
        Args:
            filter_type: 'BF', 'OD', or 'Overall'
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Clear BF history if needed
            if filter_type in ['BF', 'Overall']:
                cursor.execute("DELETE FROM bf_threshold_history")
            
            # Clear OD history if needed
            if filter_type in ['OD', 'Overall']:
                cursor.execute("DELETE FROM od_threshold_history")
            
            self.connection.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            print(f"❌ Error clearing threshold history: {e}")
            return False
