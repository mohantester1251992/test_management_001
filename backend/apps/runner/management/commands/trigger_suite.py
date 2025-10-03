from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from backend.apps.runner.models import Run
from backend.apps.runner.tasks import run_test
from backend.apps.suites.models import Suite
from backend.apps.projects.models import Environment
from backend.apps.testcases.models import Dataset


class Command(BaseCommand):
    help = "Trigger a suite execution via Celery runner."

    def add_arguments(self, parser):
        parser.add_argument("--suite", type=int, required=True)
        parser.add_argument("--env", type=int, required=False)
        parser.add_argument("--dataset", type=int, required=False)

    def handle(self, *args, **options):
        try:
            suite = Suite.objects.get(id=options["suite"])
        except Suite.DoesNotExist as exc:
            raise CommandError("Suite not found") from exc
        environment = None
        if options.get("env"):
            environment = Environment.objects.get(id=options["env"])
        else:
            environment = suite.default_environment or suite.project.environments.first()
        dataset = None
        if options.get("dataset"):
            dataset = Dataset.objects.get(id=options["dataset"])
        run = Run.objects.create(project=suite.project, suite=suite, environment=environment, dataset=dataset)
        run_test.delay(run.id)
        self.stdout.write(self.style.SUCCESS(f"Triggered run {run.id}"))
