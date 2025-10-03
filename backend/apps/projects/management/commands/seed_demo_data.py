from __future__ import annotations

from django.core.management.base import BaseCommand

from backend.apps.accounts.models import User
from backend.apps.organizations.models import Membership, Organization
from backend.apps.projects.models import Environment, Locator, Project, Secret
from backend.apps.suites.models import Suite, SuiteTestCase
from backend.apps.testcases.models import Dataset, TestCase, TestStep


class Command(BaseCommand):
    help = "Seed demo data including sample project, tests, and suites."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(email="demo@example.com", defaults={"first_name": "Demo", "is_staff": True})
        user.set_password("demo1234")
        user.save()
        org, _ = Organization.objects.get_or_create(name="Demo Labs", defaults={"created_by": user})
        Membership.objects.get_or_create(organization=org, user=user, defaults={"role": Membership.ROLE_OWNER})
        project, _ = Project.objects.get_or_create(
            organization=org,
            slug="demo",
            defaults={
                "name": "Demo Shop",
                "description": "Sample storefront used for UI automation demos.",
                "default_base_url": "https://example.com",
                "created_by": user,
            },
        )
        env, _ = Environment.objects.get_or_create(
            project=project,
            slug="staging",
            defaults={"name": "Staging", "base_url": "https://staging.example.com"},
        )
        secret, _ = Secret.objects.get_or_create(project=project, name="API Token", key="API_TOKEN", defaults={"created_by": user})
        secret.set_value("secret-token")
        secret.save()
        locator, _ = Locator.objects.get_or_create(project=project, name="Login Button", defaults={"strategy": Locator.CSS, "value": "button[type=submit]"})
        test_case, _ = TestCase.objects.get_or_create(
            project=project,
            slug="checkout",
            defaults={"name": "Complete checkout", "created_by": user, "description": "End-to-end checkout happy path."},
        )
        if not test_case.steps.exists():
            TestStep.objects.create(test_case=test_case, order=1, action="navigate", parameters={"url": "/"})
            TestStep.objects.create(test_case=test_case, order=2, action="click", locator=locator, parameters={})
            TestStep.objects.create(test_case=test_case, order=3, action="assert", locator=locator, assertion={"text": "Checkout"})
        dataset, _ = Dataset.objects.get_or_create(project=project, slug="smoke-data", defaults={"name": "Smoke data", "data": [{"email": "demo@example.com"}]})
        suite, _ = Suite.objects.get_or_create(project=project, slug="smoke", defaults={"name": "Smoke", "created_by": user, "default_environment": env})
        SuiteTestCase.objects.get_or_create(suite=suite, test_case=test_case, defaults={"dataset": dataset, "order": 1})
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
