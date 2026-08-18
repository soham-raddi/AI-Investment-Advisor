"""Database connection module for Databricks SQL Warehouse."""

import os
from databricks.sdk import WorkspaceClient
import pandas as pd
import streamlit as st


class DatabaseConnection:
    """Manages SQL Warehouse connections using Databricks SDK."""
    
    def __init__(self):
        self.client = None
        self.warehouse_id = '3614b1e06616ee4e'
        self._connect()
    
    def _connect(self):
        """Establish connection using Databricks SDK."""
        try:
            # Use Databricks SDK which handles app authentication automatically
            self.client = WorkspaceClient()
        except Exception as e:
            st.error(f"Failed to initialize Databricks client: {str(e)}")
            raise
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results as a pandas DataFrame.
        
        Args:
            query: SQL query string
            params: Optional dictionary of query parameters for parameterization
            
        Returns:
            pandas DataFrame with query results
        """
        try:
            # Replace parameterized queries with actual values
            if params:
                for key, value in params.items():
                    # Simple parameter replacement (for basic string/number params)
                    if isinstance(value, str):
                        query = query.replace(f':{key}', f"'{value}'")
                    else:
                        query = query.replace(f':{key}', str(value))
            
            # Execute SQL using Databricks SDK
            result = self.client.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout='30s'
            )
            
            # Convert result to pandas DataFrame
            if result.result and result.result.data_array:
                # Get column names
                columns = [col.name for col in result.manifest.schema.columns]
                # Get data rows
                data = result.result.data_array
                df = pd.DataFrame(data, columns=columns)
                return df
            else:
                # Return empty DataFrame with proper columns if available
                if result.manifest and result.manifest.schema:
                    columns = [col.name for col in result.manifest.schema.columns]
                    return pd.DataFrame(columns=columns)
                return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            st.error(f"Query: {query}")
            raise
    
    def close(self):
        """Close the database connection."""
        pass  # SDK client doesn't need explicit close


@st.cache_resource
def get_database_connection():
    """Get a cached database connection instance."""
    return DatabaseConnection()