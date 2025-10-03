from __future__ import annotations

import logging
from datetime import datetime

from celery import shared_task
from django.utils import timezone

from backend.apps.integrations.slack import SlackNotifier
from backend.apps.integrations.webhooks import WebhookClient
from backend.apps.suites.models import Schedule, Suite
from backend.apps.testcases.models import TestCase

from .models import Run, RunLog
from .playwright_runner import execute_test_case

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def schedule_suites(self):
    now = timezone.now()
    for schedule in Schedule.objects.filter(is_active=True):
        if schedule.next_run_at and schedule.next_run_at > now:
            continue
        suite = schedule.suite
        environment = suite.default_environment or suite.project.environments.first()
        if not environment:
            logger.warning("Suite %s has no environment", suite)
            continue
        run = Run.objects.create(
            project=suite.project,
            suite=suite,
            environment=environment,
            schedule=schedule,
        )
        logger.info("Scheduled run %s for suite %s", run.id, suite.name)
        run_test.delay(run.id)
        schedule.next_run_at = now + timezone.timedelta(minutes=5)
        schedule.save(update_fields=["next_run_at"])


@shared_task(bind=True, max_retries=3)
def run_test(self, run_id: int):
    try:
        run = Run.objects.get(id=run_id)
    except Run.DoesNotExist:
        logger.error("Run %s does not exist", run_id)
        return

    run.mark_started()
    notifier = SlackNotifier(run.project)
    webhooks = WebhookClient(run.project)

    try:
        summary = {"total": 0, "passed": 0, "failed": 0}
        suite_tests = list(run.suite.suite_tests.order_by("order")) if run.suite else []
        for suite_test in suite_tests:
            test_case: TestCase = suite_test.test_case
            result = execute_test_case(test_case, run.environment)
            summary["total"] += 1
            if result["status"] == "passed":
                summary["passed"] += 1
            else:
                summary["failed"] += 1
            RunLog.objects.create(run=run, level="info", message=result["message"], metadata=result)
        if not suite_tests:
            RunLog.objects.create(run=run, level="warning", message="No tests associated with run")
        status = Run.STATUS_PASSED if summary["failed"] == 0 else Run.STATUS_FAILED
        run.mark_completed(status=status, summary=summary)
        notifier.notify_run(run)
        webhooks.notify_run(run)
    except Exception as exc:  # pragma: no cover - safety
        logger.exception("Run %s failed", run.id)
        RunLog.objects.create(run=run, level="error", message=str(exc))
        run.mark_completed(Run.STATUS_FAILED)
        notifier.notify_run(run)
        webhooks.notify_run(run)
        raise self.retry(exc=exc, countdown=30)
