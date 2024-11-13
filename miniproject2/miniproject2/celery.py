# project_name/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniproject2.settings')

# Create a new Celery instance and set its name to the project name
app = Celery('miniproject2')

# Load configuration from Django settings, using a prefix to identify Celery settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in each installed Django app's tasks.py file.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
