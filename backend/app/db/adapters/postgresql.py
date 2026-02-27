from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.adapters.base import BaseDatabaseAdapter


class PostgreSQLAdapter(BaseDatabaseAdapter):
    """PostgreSQL-specific database adapter"""

    def __init__(self, session: Session):
        super().__init__(session)

    def optimize_query(self, query):
        """
        Apply PostgreSQL-specific optimizations
        - Use EXPLAIN ANALYZE for query planning
        - Leverage advanced indexing (GIN, GiST)
        """
        return query

    def get_database_info(self) -> Dict[str, Any]:
        """Get PostgreSQL-specific information"""
        result = self.session.execute(text("SELECT version()"))
        version = result.scalar()

        # Get table sizes
        result = self.session.execute(text("""
            SELECT
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename IN ('checkpoints', 'checkpoint_blobs', 'checkpoint_writes')
        """))
        table_sizes = {row[0]: row[1] for row in result}

        return {
            "type": "postgresql",
            "version": version,
            "table_sizes": table_sizes,
            "features": {
                "json_support": True,
                "jsonb_support": True,
                "full_text_search": True,
                "advanced_indexing": True
            }
        }

    def get_checkpoint_stats(self, thread_id: str) -> Dict[str, Any]:
        """Get PostgreSQL-optimized statistics for a thread"""
        result = self.session.execute(text("""
            SELECT
                COUNT(*) as checkpoint_count,
                COUNT(DISTINCT checkpoint_id) as unique_checkpoints,
                SUM(jsonb_array_length(checkpoint::jsonb)) as total_checkpoint_keys,
                AVG(jsonb_array_length(checkpoint::jsonb)) as avg_checkpoint_keys
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
        Search within JSON checkpoint data using PostgreSQL JSONB operators
        Example: json_path = 'channel_values,messages'
        """
        # PostgreSQL uses -> and ->> operators for JSON
        path_parts = json_path.strip('$.').split('.')

        result = self.session.execute(text("""
            SELECT checkpoint_id, checkpoint
            FROM checkpoints
            WHERE thread_id = :thread_id
            AND checkpoint::jsonb #> :json_path = to_jsonb(:search_value::text)
        """), {
            "thread_id": thread_id,
            "json_path": '{' + ','.join(path_parts) + '}',
            "search_value": str(search_value)
        })

        return [{"checkpoint_id": row[0], "checkpoint": row[1]} for row in result]

    def analyze_checkpoint_performance(self, thread_id: str) -> Dict[str, Any]:
        """Analyze checkpoint query performance using EXPLAIN"""
        result = self.session.execute(text("""
            EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
            SELECT * FROM checkpoints WHERE thread_id = :thread_id
        """), {"thread_id": thread_id})

        explain_result = result.scalar()
        return {
            "query_plan": explain_result,
            "thread_id": thread_id
        }
