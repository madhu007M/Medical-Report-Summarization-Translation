import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db import Base, get_db
from backend.app.main import app


@pytest.fixture(scope="session")
def db_path():
    """Create temporary SQLite database for tests."""
    _, path = tempfile.mkstemp(suffix=".db")
    yield path
    # On Windows, SQLite may still hold a file handle briefly; ignore the error
    try:
        if os.path.exists(path):
            os.remove(path)
    except PermissionError:
        pass  # safe to ignore — temp file is cleaned up by the OS eventually


@pytest.fixture
def test_db(db_path):
    """Provide test database session."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()  # release the SQLite file handle before teardown (critical on Windows)


@pytest.fixture
def client(test_db):
    """Provide FastAPI test client with mocked database."""
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_upload_file():
    """Mock FastAPI UploadFile."""
    from io import BytesIO
    mock_file = MagicMock()
    mock_file.filename = "test_report.txt"
    mock_file.content_type = "text/plain"
    mock_file.file = BytesIO(b"Patient presents with fever and cough.")
    return mock_file
