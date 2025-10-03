from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from backend.apps.testcases.models import TestCase


class Command(BaseCommand):
    help = "Mark tests as flaky based on historical run results."

    def handle(self, *args, **options):
        queryset = TestCase.objects.annotate(
            failure_count=Count("run_steps", filter=Q(run_steps__run__status="failed")),
            pass_count=Count("run_steps", filter=Q(run_steps__run__status="passed")),
        )
        updated = 0
        for test_case in queryset:
            total = test_case.failure_count + test_case.pass_count
            if total == 0:
                continue
            failure_rate = test_case.failure_count / total
            if failure_rate > 0.3 and not test_case.tags:
                test_case.tags = ["flaky"]
                test_case.save(update_fields=["tags"])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} flaky tests"))
