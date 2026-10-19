import os

os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
from main import app, get_db


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=test_engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    database.Base.metadata.create_all(bind=test_engine) 
    app.dependency_overrides[get_db] = override_get_db 
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    database.Base.metadata.drop_all(bind=test_engine) 