"""
Database manager for warranty database interactions.
Handles MySQL connections and queries using MCP server.
"""

from typing import List, Dict, Any, Optional
import mysql.connector
from src.utils.error_handler import ErrorHandler

class DatabaseManager:
    """Manages warranty database connections and queries"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.error_handler = ErrorHandler(config, logger)
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.database.host,
                port=self.config.database.port,
                user=self.config.database.user,
                password=self.config.database.password,
                database=self.config.database.name,
                autocommit=True
            )
            self.logger.info("Connected to warranty database")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Disconnected from warranty database")
    
    def get_all_group_ids(self) -> List[str]:
        """Get all unique group IDs from the database"""
        query = """
        SELECT DISTINCT Web_Product_Group_ID 
        FROM nav_items 
        WHERE Web_Product_Group_ID IS NOT NULL 
        AND Web_Product_Group_ID != ''
        ORDER BY Web_Product_Group_ID
        """
        
        results = self._execute_query(query, fetch_all=True)
        return [row['Web_Product_Group_ID'] for row in results]
    
    def get_group_data(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get all data for a specific group ID"""
        # Get main product data
        product_query = """
        SELECT * FROM nav_items 
        WHERE Web_Product_Group_ID = %s
        """
        
        products = self._execute_query(product_query, (group_id,), fetch_all=True)
        if not products:
            return None
        
        # Get component data for all products in group
        product_nos = [product['No_'] for product in products]
        placeholders = ','.join(['%s'] * len(product_nos))
        
        component_query = f"""
        SELECT * FROM nav_bom_components 
        WHERE Parent_Item_No_ IN ({placeholders})
        ORDER BY Parent_Item_No_, RANK
        """
        
        components = self._execute_query(component_query, product_nos, fetch_all=True)
        
        return {
            'group_id': group_id,
            'products': products,
            'components': components
        }
    
    def _execute_query(self, query: str, params: tuple = None, fetch_all: bool = False):
        """Execute a database query with error handling"""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
