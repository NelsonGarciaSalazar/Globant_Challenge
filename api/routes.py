from core.services import DataIngestionService
from flask import Blueprint, jsonify, request

router = Blueprint("routes", __name__)
service = DataIngestionService()

@router.route("/upload-files", methods=["POST"])
def upload_files():
    if request.method == "OPTIONS":
        return '', 204  # respuesta sin contenido para preflight
    results = {}

    try:
        service.load_departments()
        results["departments"] = "ok"
    except Exception as e:
        results["departments"] = f"error: {str(e)}"

    try:
        service.load_jobs()
        results["jobs"] = "ok"
    except Exception as e:
        results["jobs"] = f"error: {str(e)}"

    try:
        service.load_employees()
        results["hired_employees"] = "ok"
    except Exception as e:
        results["hired_employees"] = f"error: {str(e)}"

    return jsonify(results)

@router.route("/upload-batch", methods=["POST"])
def upload_batch():
    from datetime import datetime
    from infra.db.models import HiredEmployee, Department, Job
    from infra.db.connection import SessionLocal

    data = request.get_json()

    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"error": "El cuerpo debe ser una lista JSON de empleados"}), 400

    if len(data) > 1000:
        return jsonify({"error": "El máximo permitido es 1000 empleados"}), 400

    session = SessionLocal()
    inserted = 0
    errors = []

    # Cache IDs existentes
    dept_ids = {d.id for d in session.query(Department.id).all()}
    job_ids = {j.id for j in session.query(Job.id).all()}

    try:
        for idx, row in enumerate(data):
            try:
                if not all(k in row for k in ["id", "name", "datetime", "department_id", "job_id"]):
                    errors.append({"row": idx, "error": "Faltan campos obligatorios"})
                    continue

                if row["department_id"] not in dept_ids:
                    errors.append({"row": idx, "error": f"department_id {row['department_id']} no existe"})
                    continue

                if row["job_id"] not in job_ids:
                    errors.append({"row": idx, "error": f"job_id {row['job_id']} no existe"})
                    continue

                emp = HiredEmployee(
                    id=int(row["id"]),
                    name=row["name"].strip(),
                    datetime=datetime.fromisoformat(row["datetime"].replace("Z", "+00:00")),
                    department_id=int(row["department_id"]),
                    job_id=int(row["job_id"])
                )
                session.add(emp)
                inserted += 1

            except Exception as e:
                errors.append({"row": idx, "error": str(e)})

        session.commit()
        return jsonify({"inserted": inserted, "errors": errors}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@router.route("/departments", methods=["POST"])
def insert_departments():
    from infra.db.models import Department
    from infra.db.connection import SessionLocal

    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "El cuerpo debe ser una lista JSON"}), 400

    session = SessionLocal()
    inserted = 0
    try:
        for row in data:
            if not all(k in row for k in ["id", "department"]):
                continue
            dept = Department(id=int(row["id"]), department=row["department"].strip())
            session.add(dept)
            inserted += 1
        session.commit()
        return jsonify({"inserted": inserted}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@router.route("/jobs", methods=["POST"])
def insert_jobs():
    from infra.db.models import Job
    from infra.db.connection import SessionLocal

    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "El cuerpo debe ser una lista JSON"}), 400

    session = SessionLocal()
    inserted = 0
    try:
        for row in data:
            if not all(k in row for k in ["id", "job"]):
                continue
            job = Job(id=int(row["id"]), job=row["job"].strip())
            session.add(job)
            inserted += 1
        session.commit()
        return jsonify({"inserted": inserted}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
