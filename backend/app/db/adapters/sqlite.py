from typing import Dict, Any
from sqlalchemy.orm import Session
from app.db.adapters.base import BaseDatabaseAdapter


class SQLiteAdapter(BaseDatabaseAdapter):
    """SQLite-specific database adapter"""

    def __init__(self, session: Session):
        super().__init__(session)

    def optimize_query(self, query):
        """
        Apply SQLite-specific optimizations
        - Use PRAGMA statements for performance tuning
        - Optimize for single-user scenarios
        """
        return query

    def get_database_info(self) -> Dict[str, Any]:
        """Get SQLite-specific information"""
        result = self.session.execute("SELECT sqlite_version()")
        version = result.scalar()

        # Get table info
        result = self.session.execute("""
            SELECT name, sql FROM sqlite_master
            WHERE type='table'
            AND name IN ('checkpoints', 'checkpoint_blobs', 'checkpoint_writes')
        """)
        tables = {row[0]: row[1] for row in result}

        # Get database size
        result = self.session.execute("PRAGMA page_count")
        page_count = result.scalar()
        result = self.session.execute("PRAGMA page_size")
        page_size = result.scalar()
        db_size_mb = (page_count * page_size) / (1024 * 1024)

        return {
            "type": "sqlite",
            "version": version,
            "database_size_mb": round(db_size_mb, 2),
            "tables": list(tables.keys()),
            "features": {
                "json_support": True,
                "full_text_search": True,
                "lightweight": True
            }
        }

    def get_checkpoint_stats(self, thread_id: str) -> Dict[str, Any]:
        """Get SQLite-optimized statistics for a thread"""
        result = self.session.execute("""
            SELECT
                COUNT(*) as checkpoint_count,
                COUNT(DISTINCT checkpoint_id) as unique_checkpoints
            FROM checkpoints
            WHERE thread_id = :thread_id
        """, {"thread_id": thread_id})

        row = result.fetchone()
        return {
            "checkpoint_count": row[0],
            "unique_checkpoints": row[1]
        }

    def search_in_checkpoint_json(
        self,
        thread_id: str,
        json_path: str,
        search_value: Any
    ) -> list:
        """
        Search within JSON checkpoint data using SQLite JSON functions
        Example: json_path = '$.channel_values.messages'
        """
        result = self.session.execute("""
            SELECT checkpoint_id, checkpoint
            FROM checkpoints
            WHERE thread_id = :thread_id
            AND json_extract(checkpoint, :json_path) = :search_value
        """, {
            "thread_id": thread_id,
            "json_path": json_path,
            "search_value": search_value
        })

        return [{"checkpoint_id": row[0], "checkpoint": row[1]} for row in result]

    def optimize_database(self):
        """Run SQLite-specific optimization commands"""
        # Enable WAL mode for better concurrency
        self.session.execute("PRAGMA journal_mode=WAL")

        # Optimize database
        self.session.execute("PRAGMA optimize")

        # Analyze tables for query planner
        self.session.execute("ANALYZE")

        self.session.commit()

    def vacuum_database(self):
        """Reclaim unused space in SQLite database"""
        self.session.execute("VACUUM")
        self.session.commit()
