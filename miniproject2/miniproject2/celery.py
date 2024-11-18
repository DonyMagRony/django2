from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from django_celery_beat.models import PeriodicTask, IntervalSchedule

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

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Set up the daily report task to run once every day
    schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)
    
    # Ensure that the periodic task doesn't get recreated if it already exists
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Daily Report Summary',
        task='notifications.tasks.daily_report_summary',
    )

    # Set up the weekly performance summary task to run once every week
    schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.WEEKS)
    
    # Ensure that the periodic task doesn't get recreated if it already exists
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Weekly Performance Summary',
        task='notifications.tasks.weekly_performance_summary',
    )
