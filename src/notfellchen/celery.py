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
    'daily-unchecked-deactivation': {
        'task': 'admin.daily_unchecked_deactivation',
        'schedule': crontab(hour=1),
    },
    'daily-404-deactivation': {
        'task': 'admin.deactivate_404_adoption_notices',
        'schedule': crontab(hour=3),
    },
    'daily-fedi-post': {
        'task': 'social_media.post_fedi',
        'schedule': crontab(hour=19),
    },

}

if settings.HEALTHCHECKS_URL is not None and settings.HEALTHCHECKS_URL != "":
    # If a healthcheck is configured, this will send an hourly ping to the healthchecks server
    app.conf.beat_schedule['hourly-healthcheck'] = {'task': 'tools.healthcheck',
                                                    'schedule': crontab(minute=43),
                                                    }
