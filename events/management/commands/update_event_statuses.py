# events/management/commands/update_event_statuses.py
from django.core.management.base import BaseCommand
from events.models import Event


class Command(BaseCommand):
    help = "Actualitza automàticament els estats dels esdeveniments (scheduled -> live, live -> finished)."

    def handle(self, *args, **options):
        stats = Event.auto_update_statuses()
        self.stdout.write(self.style.SUCCESS("Estats actualitzats correctament."))
        self.stdout.write(f" - scheduled -> live: {stats['scheduled_to_live']}")
        self.stdout.write(f" - live -> finished: {stats['live_to_finished']}")
