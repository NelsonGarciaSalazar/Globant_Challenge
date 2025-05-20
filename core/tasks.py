from infra.broker.celery_config import celery_app
from core.services import DataIngestionService

@celery_app.task(name="load_employees_task", ignore_result=False)
def load_employees_task(start=0, limit=1000, skip_existing=True):
    service = DataIngestionService()
    return service.load_employees(start=start, limit=limit, skip_existing=skip_existing)
