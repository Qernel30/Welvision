"""
Database operations for threshold history
"""

import mysql.connector
from datetime import datetime


class ThresholdDatabase:
    """Handles database operations for threshold history."""
    
    def __init__(self, host='localhost', user='root', password='root', database='welvision_db'):
        """
        Initialize database connection parameters.
        
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
    
    def save_bf_thresholds(self, employee_id, defect_thresholds, model_confidence, model_name):
        """
        Save BF threshold settings to database.
        
        Args:
            employee_id: Employee ID
            defect_thresholds: Dictionary of defect thresholds {defect_name: value}
            model_confidence: Model confidence threshold (0-1)
            model_name: Name of the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            cursor = connection.cursor()
            
            # Format defect thresholds as string: "defect1:100%, defect2:50%"
            defect_threshold_str = ", ".join([f"{k}:{v}%" for k, v in defect_thresholds.items()])
            
            # Insert into bf_threshold_history
            query = """
                INSERT INTO bf_threshold_history 
                (employee_id, defect_threshold, model_threshold, model_name)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query, (employee_id, defect_threshold_str, model_confidence, model_name))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"❌ Database error saving BF thresholds: {e}")
            return False
        except Exception as e:
            print(f"❌ Error saving BF thresholds: {e}")
            return False
    
    def save_od_thresholds(self, employee_id, defect_thresholds, model_confidence, model_name):
        """
        Save OD threshold settings to database.
        
        Args:
            employee_id: Employee ID
            defect_thresholds: Dictionary of defect thresholds {defect_name: value}
            model_confidence: Model confidence threshold (0-1)
            model_name: Name of the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            cursor = connection.cursor()
            
            # Format defect thresholds as string: "defect1:100%, defect2:50%"
            defect_threshold_str = ", ".join([f"{k}:{v}%" for k, v in defect_thresholds.items()])
            
            # Insert into od_threshold_history
            query = """
                INSERT INTO od_threshold_history 
                (employee_id, defect_threshold, model_threshold, model_name)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query, (employee_id, defect_threshold_str, model_confidence, model_name))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"❌ Database error saving OD thresholds: {e}")
            return False
        except Exception as e:
            print(f"❌ Error saving OD thresholds: {e}")
            return False
