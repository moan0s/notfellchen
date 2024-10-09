from notfellchen.celery import app as celery_app
from .tools.admin import clean_locations

@celery_app.task(name="admin.clean_locations")
def task_clean_locations():
    clean_locations()
