"""
Basic tests for FlintBloom
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.config import get_settings

# Test database URL (SQLite in-memory)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_info():
    """Test API info endpoint"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "features" in data
    assert "supported_databases" in data
    assert "mysql" in data["supported_databases"]
    assert "postgresql" in data["supported_databases"]
    assert "sqlite" in data["supported_databases"]


def test_list_threads_empty(test_db):
    """Test listing threads when database is empty"""
    response = client.get("/api/v1/offline/threads")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["threads"] == []


def test_database_info(test_db):
    """Test database info endpoint"""
    response = client.get("/api/v1/offline/database/info")
    assert response.status_code == 200
    data = response.json()
    assert "type" in data


def test_realtime_active_threads():
    """Test listing active real-time threads"""
    response = client.get("/api/v1/realtime/threads")
    assert response.status_code == 200
    data = response.json()
    assert "threads" in data
    assert "count" in data


def test_checkpoint_not_found(test_db):
    """Test getting non-existent checkpoint"""
    response = client.get(
        "/api/v1/offline/threads/nonexistent/checkpoints/fake/trace"
    )
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
