import pytest
import pandas as pd
from unittest.mock import MagicMock
from core.services import DataIngestionService
from infra.db.connection import SessionLocal
from infra.db.models import Department, Job, HiredEmployee

@pytest.fixture
def service():
    svc = DataIngestionService()
    svc.blob_client = MagicMock()
    return svc

@pytest.fixture(autouse=True)
def force_sqlite_session(monkeypatch):
    from tests.conftest import SessionLocal as test_SessionLocal
    monkeypatch.setattr("core.services.SessionLocal", test_SessionLocal)

@pytest.fixture(autouse=True)
def reset_database():
    from infra.db.models import Base
    from tests.conftest import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_load_departments_success(service):
    df = pd.DataFrame({"id": [1, 2], "department": ["HR", "IT"]})
    csv_bytes = df.to_csv(index=False, header=False).encode()
    service.blob_client.download_file.return_value = csv_bytes

    summary = service.load_departments()

    session = SessionLocal()
    rows = session.query(Department).all()
    assert len(rows) == 2
    assert summary == {"processed": 2, "inserted": 2, "already_exists": 0}
    session.close()

def test_load_jobs_success(service):
    df = pd.DataFrame({"id": [1, 2], "job": ["Manager", "Engineer"]})
    csv_bytes = df.to_csv(index=False, header=False).encode()
    service.blob_client.download_file.return_value = csv_bytes

    summary = service.load_jobs()

    session = SessionLocal()
    rows = session.query(Job).all()
    assert len(rows) == 2
    assert summary == {"processed": 2, "inserted": 2, "already_exists": 0}
    session.close()

def test_load_employees_success(service):
    session = SessionLocal()
    session.add_all([
        Department(id=1, department="HR"),
        Job(id=1, job="Manager")
    ])
    session.commit()

    df = pd.DataFrame({
        "id": [1, 2],
        "name": ["Alice", "Bob"],
        "datetime": ["2021-01-01T10:00:00Z", "2021-01-02T12:00:00Z"],
        "department_id": [1, 1],
        "job_id": [1, 1]
    })
    csv_bytes = df.to_csv(index=False, header=False).encode()
    service.blob_client.download_file.return_value = csv_bytes

    summary = service.load_employees()

    rows = session.query(HiredEmployee).all()
    assert len(rows) == 2
    assert summary["inserted"] == 2
    assert summary["errors"] == 0
    assert summary["already_exists"] == 0
    session.close()
