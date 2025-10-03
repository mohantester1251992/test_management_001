from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from backend.apps.projects.models import Environment, Project
from backend.apps.testcases.models import Dataset, TestCase


class SuiteQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self
        return self.filter(project__organization__memberships__user=user).distinct()


class Suite(models.Model):
    project = models.ForeignKey(Project, related_name="suites", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    retries = models.PositiveIntegerField(default=0)
    parallelism = models.PositiveIntegerField(default=1)
    default_environment = models.ForeignKey(Environment, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.JSONField(default=list, blank=True)

    objects = SuiteQuerySet.as_manager()

    class Meta:
        unique_together = ("project", "slug")
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    @property
    def active_schedules(self):
        return self.schedules.filter(is_active=True)


class SuiteTestCase(models.Model):
    suite = models.ForeignKey(Suite, related_name="suite_tests", on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, related_name="suite_tests", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    dataset = models.ForeignKey(Dataset, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("suite", "test_case")
        ordering = ["order"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.suite} -> {self.test_case}"


class Schedule(models.Model):
    suite = models.ForeignKey(Suite, related_name="schedules", on_delete=models.CASCADE)
    cron = models.CharField(max_length=120)
    timezone = models.CharField(max_length=64, default="UTC")
    is_active = models.BooleanField(default=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    human_readable = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["suite", "cron"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.suite.name} @ {self.cron}"


class SuiteNotification(models.Model):
    CHANNEL_SLACK = "slack"
    CHANNEL_EMAIL = "email"
    CHANNEL_WEBHOOK = "webhook"

    CHANNEL_CHOICES = [
        (CHANNEL_SLACK, "Slack"),
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_WEBHOOK, "Webhook"),
    ]

    suite = models.ForeignKey(Suite, related_name="notifications", on_delete=models.CASCADE)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    target = models.CharField(max_length=255)
    on_failure_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["suite", "channel"]


class CalendarEvent(models.Model):
    suite = models.ForeignKey(Suite, related_name="calendar_events", on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, related_name="calendar_events", on_delete=models.CASCADE)
    run_at = models.DateTimeField()
    status = models.CharField(max_length=20, default="scheduled")

    class Meta:
        ordering = ["run_at"]
