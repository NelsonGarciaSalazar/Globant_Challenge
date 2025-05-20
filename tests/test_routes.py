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
    monkeypatch.setattr("api.routes.SessionLocal", test_SessionLocal)

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

def test_upload_files_endpoint(client, monkeypatch):
    # Mock service methods
    monkeypatch.setattr("api.routes.service.load_departments", lambda: {"processed": 2, "inserted": 2, "already_exists": 0})
    monkeypatch.setattr("api.routes.service.load_jobs", lambda: {"processed": 2, "inserted": 2, "already_exists": 0})
    monkeypatch.setattr("api.routes.service.load_employees", lambda start=0, limit=1000, skip_existing=True: {"processed": 2, "inserted": 2, "already_exists": 0, "errors": 0, "error_ids": []})

    response = client.post("/upload-files")
    assert response.status_code == 200
    data = response.get_json()

    assert data["departments"]["inserted"] == 2
    assert data["jobs"]["inserted"] == 2
    assert data["hired_employees"][0]["inserted"] == 2

def test_upload_hired_employees_endpoint(client, monkeypatch):
    from uuid import uuid4
    fake_task_id = str(uuid4())

    class FakeAsyncResult:
        id = fake_task_id

        def __init__(self, *args, **kwargs):
            self.status = "accepted"

    monkeypatch.setattr("core.tasks.load_employees_task.delay", lambda **kwargs: FakeAsyncResult())

    response = client.post("/upload-hired-employees?start=0&limit=1000")
    assert response.status_code == 202
    data = response.get_json()
    assert "task_id" in data
    assert data["status"] == "accepted"

def test_upload_files_with_error(client, monkeypatch):
    monkeypatch.setattr("api.routes.service.load_departments", lambda: (_ for _ in ()).throw(Exception("departments error")))
    monkeypatch.setattr("api.routes.service.load_jobs", lambda: {"processed": 2, "inserted": 2, "already_exists": 0})
    monkeypatch.setattr("api.routes.service.load_employees", lambda **kwargs: {"processed": 1, "inserted": 1, "already_exists": 0, "errors": 0, "error_ids": []})

    response = client.post("/upload-files")
    assert response.status_code == 200
    data = response.get_json()

    assert "error" in data["departments"]
    assert "jobs" in data
    assert isinstance(data["hired_employees"], list)
