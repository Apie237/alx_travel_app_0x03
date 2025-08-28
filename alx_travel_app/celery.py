
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')

app = Celery('alx_travel_app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Optional: Configure task routes
app.conf.task_routes = {
    'listings.tasks.send_booking_confirmation_email': {'queue': 'emails'},
}

# Optional: Configure task options
app.conf.task_annotations = {
    'listings.tasks.send_booking_confirmation_email': {
        'rate_limit': '50/m',
        'time_limit': 300,
    }
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')