from celery.app import shared_task
from django.utils import timezone
from notfellchen.celery import app as celery_app
from .mail import send_notification_email
from .tools.admin import clean_locations, deactivate_unchecked_adoption_notices, deactivate_404_adoption_notices
from .tools.misc import healthcheck_ok
from .models import Location, AdoptionNotice, Timestamp


def set_timestamp(key: str):
    try:
        ts = Timestamp.objects.get(key=key)
        ts.timestamp = timezone.now()
        ts.save()
    except Timestamp.DoesNotExist:
        Timestamp.objects.create(key=key, timestamp=timezone.now())


@celery_app.task(name="admin.clean_locations")
def task_clean_locations():
    clean_locations()
    set_timestamp("task_clean_locations")


@celery_app.task(name="admin.daily_unchecked_deactivation")
def task_deactivate_unchecked():
    deactivate_unchecked_adoption_notices()
    set_timestamp("task_daily_unchecked_deactivation")


@celery_app.task(name="admin.deactivate_404_adoption_notices")
def task_deactivate_unchecked():
    deactivate_404_adoption_notices()
    set_timestamp("task_deactivate_404_adoption_notices")


@celery_app.task(name="commit.add_location")
def add_adoption_notice_location(pk):
    instance = AdoptionNotice.objects.get(pk=pk)
    Location.add_location_to_object(instance)
    set_timestamp("add_adoption_notice_location")


@celery_app.task(name="tools.healthcheck")
def task_healthcheck():
    healthcheck_ok()
    set_timestamp("task_healthcheck")


@shared_task
def task_send_notification_email(notification_pk):
    send_notification_email(notification_pk)
