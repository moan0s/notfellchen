import os
from celery import Celery
from celery.schedules import crontab
from notfellchen import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notfellchen.settings')

app = Celery('notfellchen')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'daily-cleanup': {
        'task': 'admin.clean_locations',
        'schedule': crontab(hour=2),
    },
    'daily-deactivation': {
        'task': 'admin.deactivate_unchecked',
        'schedule': crontab(hour=1),
    },
}

if settings.HEALTHCHECK_URL is not None and settings.HEALTHCHECK_URL != "":
    # If a healthcheck is configured, this will send an hourly ping to the healthchecks server
    app.conf.beat_schedule['hourly-healthcheck'] = {'task': 'tools.healthcheck',
                                                    'schedule': crontab(minute=32),
                                                    }
