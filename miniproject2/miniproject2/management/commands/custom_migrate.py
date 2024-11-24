from django.core.management.base import BaseCommand
from django.apps import apps
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Perform migrations excluding specific apps'

    def handle(self, *args, **kwargs):
        excluded_apps = ['analytics']
        installed_apps = [app.label for app in apps.get_app_configs()]

        for app in installed_apps:
            if app not in excluded_apps:
                self.stdout.write(f"Migrating {app}...")
                call_command('migrate', app, database='default')
