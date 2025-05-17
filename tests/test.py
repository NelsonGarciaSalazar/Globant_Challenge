def test_upload_files(client):
    response = client.post("/upload-files")
    assert response.status_code == 200
    data = response.get_json()
    assert "departments" in data
    assert "jobs" in data
    assert "hired_employees" in data

def test_upload_batch_empty(client):
    response = client.post("/upload-batch", json=[])
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_upload_batch_too_many(client):
    payload = [{"id": i, "name": "Test", "datetime": "2021-01-01T00:00:00Z", "department_id": 1, "job_id": 1} for i in range(1001)]
    response = client.post("/upload-batch", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_departments_insert(client):
    payload = [{"id": 99, "department": "TestDept"}]
    response = client.post("/departments", json=payload)
    print("DEPARTMENTS:", response.get_json())
    print("status_code:", response.status_code)
    assert response.status_code == 200

def test_jobs_insert(client):
    from infra.db.connection import SessionLocal
    from infra.db.models import Job

    session = SessionLocal()
    session.query(Job).filter(Job.id == 99).delete()
    session.commit()
    session.close()

    payload = [{"id": 99, "job": "TestJob"}]
    response = client.post("/jobs", json=payload)
    print("JOBS:", response.get_json())
    assert response.status_code == 200





