import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", broker_url)

celery_app = Celery(
    "globant_tasks",
    broker=broker_url,
    backend=backend_url
)

# ⚠️ Habilita soporte SSL si estás en rediss://
if broker_url.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": "CERT_NONE"}
if backend_url.startswith("rediss://"):
    celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": "CERT_NONE"}

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
