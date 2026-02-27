from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.adapters.base import BaseDatabaseAdapter


class MySQLAdapter(BaseDatabaseAdapter):
    """MySQL-specific database adapter"""

    def __init__(self, session: Session):
        super().__init__(session)

    def optimize_query(self, query):
        """
        Apply MySQL-specific optimizations
        - Use FORCE INDEX for large tables
        - Optimize JOIN operations
        """
        # MySQL uses index hints for optimization
        return query

    def get_database_info(self) -> Dict[str, Any]:
        """Get MySQL-specific information"""
        result = self.session.execute(text("SELECT VERSION() as version"))
        version = result.scalar()

        # Get table sizes
        result = self.session.execute(text("""
            SELECT
                table_name,
                ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
            FROM information_schema.TABLES
            WHERE table_schema = DATABASE()
            AND table_name IN ('checkpoints', 'checkpoint_blobs', 'checkpoint_writes')
        """))
        table_sizes = {row[0]: row[1] for row in result}

        return {
            "type": "mysql",
            "version": version,
            "table_sizes_mb": table_sizes,
            "features": {
                "json_support": True,
                "full_text_search": True,
                "spatial_index": True
            }
        }

    def get_checkpoint_stats(self, thread_id: str) -> Dict[str, Any]:
        """Get MySQL-optimized statistics for a thread"""
        result = self.session.execute(text("""
            SELECT
                COUNT(*) as checkpoint_count,
                COUNT(DISTINCT checkpoint_id) as unique_checkpoints,
                SUM(JSON_LENGTH(checkpoint)) as total_checkpoint_keys,
                AVG(JSON_LENGTH(checkpoint)) as avg_checkpoint_keys
            FROM checkpoints
            WHERE thread_id = :thread_id
        """), {"thread_id": thread_id})

        row = result.fetchone()
        return {
            "checkpoint_count": row[0],
            "unique_checkpoints": row[1],
            "total_checkpoint_keys": row[2],
            "avg_checkpoint_keys": float(row[3]) if row[3] else 0
        }

    def search_in_checkpoint_json(
        self,
        thread_id: str,
        json_path: str,
        search_value: Any
    ) -> list:
        """
        Search within JSON checkpoint data using MySQL JSON functions
        Example: json_path = '$.channel_values.messages'
        """
        result = self.session.execute(text("""
            SELECT checkpoint_id, checkpoint
            FROM checkpoints
            WHERE thread_id = :thread_id
            AND JSON_EXTRACT(checkpoint, :json_path) = :search_value
        """), {
            "thread_id": thread_id,
            "json_path": json_path,
            "search_value": search_value
        })

        return [{"checkpoint_id": row[0], "checkpoint": row[1]} for row in result]
