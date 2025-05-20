from core.services import DataIngestionService
from sqlalchemy import text
from infra.db.connection import SessionLocal
from flask import Blueprint, request, jsonify
from core.tasks import load_employees_task
import redis
from celery.result import AsyncResult
from celery_worker import celery_app

router = Blueprint("routes", __name__)
service = DataIngestionService()

@router.route("/")
def root():
    return "¡Hi from Azure Web App Flask in Docker!"

@router.route("/health")
def health():
    try:
        r = redis.Redis(host="redis", port=6379, socket_connect_timeout=2)
        r.ping()
        return {"status": "ok", "redis": "connected"}, 200
    except redis.ConnectionError:
        return {"status": "error", "redis": "unreachable"}, 500

@router.route("/upload-files", methods=["POST"])
def upload_files():
    employees_result = []

    try:
        departments_result = service.load_departments()
    except Exception as e:
        departments_result = {"error": str(e)}

    try:
        jobs_result = service.load_jobs()
    except Exception as e:
        jobs_result = {"error": str(e)}

    try:
        start = 0
        limit = 1000
        while True:
            summary = service.load_employees(start=start, limit=limit, skip_existing=True)
            employees_result.append(summary)
            if summary["processed"] < limit:
                break
            start += limit
    except Exception as e:
        employees_result.append({"error": str(e)})

    return jsonify({
        "departments": departments_result,
        "jobs": jobs_result,
        "hired_employees": employees_result
    })

@router.route("/upload-hired-employees", methods=["POST"])
def upload_employees():
    start = int(request.args.get("start", 0))
    limit = int(request.args.get("limit", 1000))
    task = load_employees_task.delay(start=start, limit=limit)
    return jsonify({"task_id": task.id, "status": "accepted"}), 202

@router.route("/task-list")
def task_list():
    r = redis.Redis(host="redis", port=6379, decode_responses=True)
    task_keys = sorted(r.keys("celery-task-meta-*"), reverse=True)[:20]
    tasks = []
    for key in task_keys:
        task_id = key.replace("celery-task-meta-", "")
        result = AsyncResult(task_id, app=celery_app)
        if result.status in ("SUCCESS", "FAILURE"):
            tasks.append({
                "id": task_id,
                "status": result.status,
                "result": result.result if result.ready() else None
            })
    return jsonify(tasks)

@router.route("/departments", methods=["POST"])
def insert_departments():
    try:
        summary = service.load_departments()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router.route("/jobs", methods=["POST"])
def insert_jobs():
    try:
        summary = service.load_jobs()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router.route("/report/hired-by-quarter", methods=["GET"])
def hired_by_quarter():
    session = SessionLocal()

    try:
        result = session.execute(text("""
            SELECT 
                d.department,
                j.job,
                SUM(CASE WHEN MONTH(h.datetime) BETWEEN 1 AND 3 THEN 1 ELSE 0 END) AS Q1,
                SUM(CASE WHEN MONTH(h.datetime) BETWEEN 4 AND 6 THEN 1 ELSE 0 END) AS Q2,
                SUM(CASE WHEN MONTH(h.datetime) BETWEEN 7 AND 9 THEN 1 ELSE 0 END) AS Q3,
                SUM(CASE WHEN MONTH(h.datetime) BETWEEN 10 AND 12 THEN 1 ELSE 0 END) AS Q4
            FROM hired_employees h
            JOIN departments d ON h.department_id = d.id
            JOIN jobs j ON h.job_id = j.id
            WHERE YEAR(h.datetime) = 2021
            GROUP BY d.department, j.job
            ORDER BY d.department ASC, j.job ASC;
        """))

        data = [dict(row._mapping) for row in result]
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@router.route("/report/hiring-above-average", methods=["GET"])
def hiring_above_average():
    session = SessionLocal()

    try:
        result = session.execute(text("""
            SELECT 
                d.id,
                d.department,
                COUNT(h.id) AS hired
            FROM 
                hired_employees h
            JOIN 
                departments d ON h.department_id = d.id
            WHERE 
                YEAR(h.datetime) = 2021
            GROUP BY 
                d.id, d.department
            HAVING 
                COUNT(h.id) > (
                    SELECT AVG(hired_count)
                    FROM (
                        SELECT COUNT(h.id) AS hired_count
                        FROM hired_employees h
                        WHERE YEAR(h.datetime) = 2021
                        GROUP BY h.department_id
                    ) AS dept_avg
                )
            ORDER BY hired DESC;
        """))
        data = [dict(row._mapping) for row in result]
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
