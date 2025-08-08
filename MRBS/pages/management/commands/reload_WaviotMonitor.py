# yourproject/management/commands/reload_django.py

from django.core.management.base import BaseCommand
import subprocess


class Command(BaseCommand):
    help = 'Reload the Django service'

    def handle(self, *args, **options):
        # Команда для перезагрузки сервиса
        result = subprocess.run(['sudo', '/bin/systemctl', 'restart', 'WaviotMonitor.service'], capture_output=True)

        if result.returncode != 0:
            self.stderr.write(f'Error restarting service: {result.stderr.decode()}')
        else:
            self.stdout.write('Service successfully reloaded.')