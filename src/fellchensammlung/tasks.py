from notfellchen.celery import app as celery_app
from .tools.admin import clean_locations, deactivate_unchecked_adoption_notices
from .tools.misc import healthcheck_ok
from .models import Location, AdoptionNotice


@celery_app.task(name="admin.clean_locations")
def task_clean_locations():
    clean_locations()


@celery_app.task(name="admin.deactivate_unchecked")
def task_deactivate_unchecked():
    deactivate_unchecked_adoption_notices()


@celery_app.task(name="commit.add_location")
def add_adoption_notice_location(pk):
    instance = AdoptionNotice.objects.get(pk=pk)
    Location.add_location_to_object(instance)

@celery_app.task(name="tools.healthcheck")
def task_healthcheck():
    healthcheck_ok()
