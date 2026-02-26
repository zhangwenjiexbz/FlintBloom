from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from contextlib import contextmanager
from app.core.config import get_settings

settings = get_settings()

# Create engine based on database type
engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

# SQLite specific configuration
if settings.DB_TYPE == "sqlite":
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
# MySQL SSL configuration
elif settings.DB_TYPE == "mysql" and settings.SSL_CA_PATH:
    ssl_args = {"ssl": {"ca": settings.SSL_CA_PATH}}
    if settings.SSL_CERT_PATH:
        ssl_args["ssl"]["cert"] = settings.SSL_CERT_PATH
    if settings.SSL_KEY_PATH:
        ssl_args["ssl"]["key"] = settings.SSL_KEY_PATH
    engine_kwargs["connect_args"] = ssl_args
# PostgreSQL SSL configuration
elif settings.DB_TYPE == "postgresql" and settings.SSL_CA_PATH:
    ssl_args = {
        "sslmode": "verify-ca",
        "sslrootcert": settings.SSL_CA_PATH,
    }
    if settings.SSL_CERT_PATH:
        ssl_args["sslcert"] = settings.SSL_CERT_PATH
    if settings.SSL_KEY_PATH:
        ssl_args["sslkey"] = settings.SSL_KEY_PATH
    engine_kwargs["connect_args"] = ssl_args

engine = create_engine(settings.database_url, **engine_kwargs)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session

    Usage:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session

    Usage:
        with get_db_context() as db:
            result = db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import all models here to ensure they are registered
    from app.db import models

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)


def close_db():
    """Close database connections"""
    engine.dispose()
