
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniproject2.settings')

app = Celery('miniproject2')

# Configure Celery to use the settings from Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Import here to ensure Django is fully initialized
    from django_celery_beat.models import PeriodicTask, IntervalSchedule

    schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Daily Report Summary',
        task='notifications.tasks.daily_report_summary',
    )
