"""Database schema introspection and reflection."""
import sqlite3
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SchemaIntrospector:
    """Introspects database schema and provides schema information to the agent."""
    
    def __init__(self, db_path: str, db_type: str = "sqlite"):
        """Initialize schema introspector.
        
        Args:
            db_path: Path to database file
            db_type: Type of database (sqlite, postgres, mysql)
        """
        self.db_path = db_path
        self.db_type = db_type
        self._schema_cache: Optional[Dict[str, Any]] = None
    
    def get_connection(self):
        """Get database connection."""
        if self.db_type == "sqlite":
            return sqlite3.connect(self.db_path)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def introspect_schema(self) -> Dict[str, Any]:
        """Introspect the database schema.
        
        Returns:
            Dictionary containing schema information:
            - tables: List of table information
            - relationships: Foreign key relationships
        """
        if self._schema_cache is not None:
            return self._schema_cache
        
        schema = {
            "tables": [],
            "relationships": []
        }
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.db_type == "sqlite":
                # Get all tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                tables = cursor.fetchall()
                
                for (table_name,) in tables:
                    table_info = self._get_table_info(cursor, table_name)
                    schema["tables"].append(table_info)
                
                # Get foreign key relationships
                for (table_name,) in tables:
                    relationships = self._get_foreign_keys(cursor, table_name)
                    schema["relationships"].extend(relationships)
            
            conn.close()
            self._schema_cache = schema
            logger.info(f"Introspected schema: {len(schema['tables'])} tables found")
            
        except Exception as e:
            logger.error(f"Error introspecting schema: {e}")
            raise
        
        return schema
    
    def _get_table_info(self, cursor, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table."""
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        # Get sample data (first 3 rows)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        sample_rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        # Format sample data
        sample_data = []
        for row in sample_rows:
            sample_data.append(dict(zip(column_names, row)))
        
        # Format column information
        column_info = []
        for col in columns:
            col_id, name, col_type, not_null, default_val, pk = col
            column_info.append({
                "name": name,
                "type": col_type,
                "not_null": bool(not_null),
                "default": default_val,
                "primary_key": bool(pk)
            })
        
        return {
            "name": table_name,
            "columns": column_info,
            "row_count": row_count,
            "sample_data": sample_data
        }
    
    def _get_foreign_keys(self, cursor, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key relationships for a table."""
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        
        relationships = []
        for fk in fks:
            # SQLite foreign key list format:
            # (id, seq, table, from, to, on_update, on_delete, match)
            relationships.append({
                "from_table": table_name,
                "from_column": fk[3],
                "to_table": fk[2],
                "to_column": fk[4],
                "on_update": fk[5],
                "on_delete": fk[6]
            })
        
        return relationships
    
    def get_schema_prompt(self) -> str:
        """Generate a prompt-friendly schema description."""
        schema = self.introspect_schema()
        
        prompt_parts = ["# Database Schema\n"]
        
        for table in schema["tables"]:
            prompt_parts.append(f"## Table: {table['name']}")
            prompt_parts.append(f"Row count: {table['row_count']}")
            prompt_parts.append("\nColumns:")
            
            for col in table["columns"]:
                col_desc = f"  - {col['name']} ({col['type']})"
                if col["primary_key"]:
                    col_desc += " [PRIMARY KEY]"
                if col["not_null"]:
                    col_desc += " [NOT NULL]"
                if col["default"]:
                    col_desc += f" [DEFAULT: {col['default']}]"
                prompt_parts.append(col_desc)
            
            if table["sample_data"]:
                prompt_parts.append("\nSample data:")
                for sample in table["sample_data"][:2]:  # Show max 2 samples
                    sample_str = ", ".join([f"{k}={v}" for k, v in sample.items()])
                    prompt_parts.append(f"  {sample_str}")
            
            prompt_parts.append("")
        
        if schema["relationships"]:
            prompt_parts.append("## Relationships\n")
            for rel in schema["relationships"]:
                prompt_parts.append(
                    f"- {rel['from_table']}.{rel['from_column']} -> "
                    f"{rel['to_table']}.{rel['to_column']}"
                )
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def clear_cache(self):
        """Clear the schema cache."""
        self._schema_cache = None

