from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.adapters.base import BaseDatabaseAdapter
from app.db.adapters.mysql import MySQLAdapter
from app.db.adapters.postgresql import PostgreSQLAdapter
from app.db.adapters.sqlite import SQLiteAdapter


class AdapterFactory:
    """Factory for creating database adapters based on configuration"""

    @staticmethod
    def create_adapter(session: Session) -> BaseDatabaseAdapter:
        """
        Create appropriate database adapter based on DB_TYPE setting

        Args:
            session: SQLAlchemy session

        Returns:
            Database adapter instance

        Raises:
            ValueError: If DB_TYPE is not supported
        """
        settings = get_settings()
        db_type = settings.DB_TYPE.lower()

        adapters = {
            "mysql": MySQLAdapter,
            "postgresql": PostgreSQLAdapter,
            "sqlite": SQLiteAdapter,
        }

        adapter_class = adapters.get(db_type)
        if not adapter_class:
            raise ValueError(
                f"Unsupported database type: {db_type}. "
                f"Supported types: {', '.join(adapters.keys())}"
            )

        return adapter_class(session)


def get_adapter(session: Session) -> BaseDatabaseAdapter:
    """
    Convenience function to get database adapter

    Usage:
        from app.db.adapters import get_adapter

        with get_db_context() as db:
            adapter = get_adapter(db)
            threads = adapter.get_threads()
    """
    return AdapterFactory.create_adapter(session)
