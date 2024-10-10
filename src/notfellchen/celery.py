# <your_project>/celery.py

import os
from celery import Celery
from celery.schedules import crontab

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
        'schedule': 30,
    }
}

