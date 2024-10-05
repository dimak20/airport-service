import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "airport_api_service.settings")

app = Celery("airport_api_service")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
