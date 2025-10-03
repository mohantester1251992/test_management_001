from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from backend.apps.projects.models import Locator
from backend.apps.runner.models import Run


class Command(BaseCommand):
    help = "Run basic system health checks for workers and locator health."

    def handle(self, *args, **options):
        stale_runs = Run.objects.filter(status=Run.STATUS_RUNNING, started_at__lt=timezone.now() - timezone.timedelta(hours=1))
        if stale_runs.exists():
            self.stdout.write(self.style.WARNING(f"Found {stale_runs.count()} stale runs"))
        else:
            self.stdout.write(self.style.SUCCESS("No stale runs detected"))
        unhealthy_locators = Locator.objects.filter(health_status__in=["broken", "warning"])
        self.stdout.write(f"Locator issues: {unhealthy_locators.count()}")
        self.stdout.write(self.style.SUCCESS("Health checks complete"))
