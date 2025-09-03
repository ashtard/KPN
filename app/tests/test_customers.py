from __future__ import annotations
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from app.main import app 
from app.db import Base, get_db


@pytest.fixture(scope="function")
def test_db():
    fd, path = tempfile.mkstemp(suffix= ".db")
    os.close(fd)

    
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    def _get_test_db():
        db = TestingSessionLocal()
        try:
            yield db

        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        yield

    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        if os.path.exists(path):
            os.remove(path)

@pytest.fixture()
def client(test_db):
    return TestClient(app)

def test_create_and_get_customer(client: TestClient):
    payload = {
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "phone": "+31201234567",
        "address": "Koningslaan 1, Amsterdam"
}
    r = client.post("/customers/", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    cid = created["id"]


    r2 = client.get(f"/customers/{cid}")
    assert r2.status_code == 200
    assert r2.json()["email"] == "ada@example.com"


    r3 = client.get("/customers", params={"query": "ada"})
    assert r3.status_code == 200
    assert any(c["id"] == cid for c in r3.json())


    # duplicate email
    r4 = client.post("/customers/", json=payload)
    assert r4.status_code == 409

