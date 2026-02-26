from typing import Literal, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

# Get the project root directory (backend/app/core/config.py -> go up 4 levels)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "FlintBloom"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DB_TYPE: Literal["mysql", "postgresql", "sqlite"] = "mysql"

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "agentnext"

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DATABASE: str = "agentnext"

    # SQLite
    SQLITE_PATH: str = "./data/flintbloom.db"

    # SSL Configuration (optional, for MySQL/PostgreSQL)
    SSL_CA_PATH: str = ""
    SSL_CERT_PATH: str = ""
    SSL_KEY_PATH: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Real-time
    ENABLE_REALTIME: bool = True
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def database_url(self) -> str:
        """Generate database URL based on DB_TYPE"""
        if self.DB_TYPE == "mysql":
            user = quote_plus(self.MYSQL_USER)
            password = quote_plus(self.MYSQL_PASSWORD)
            return f"mysql+pymysql://{user}:{password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb3"
        elif self.DB_TYPE == "postgresql":
            user = quote_plus(self.POSTGRES_USER)
            password = quote_plus(self.POSTGRES_PASSWORD)
            return f"postgresql+psycopg2://{user}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}"
        elif self.DB_TYPE == "sqlite":
            return f"sqlite:///{self.SQLITE_PATH}"
        else:
            raise ValueError(f"Unsupported database type: {self.DB_TYPE}")

    @property
    def redis_url(self) -> str:
        """Generate Redis URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
