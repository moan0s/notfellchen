from notfellchen.celery import app as celery_app
from .tools.admin import clean_locations
from .models import Location, AdoptionNotice


@celery_app.task(name="admin.clean_locations")
def task_clean_locations():
    clean_locations()


@celery_app.task(name="commit.add_location")
def add_adoption_notice_location(pk):
    instance = AdoptionNotice.objects.get(pk=pk)
    Location.add_location_to_object(instance)

