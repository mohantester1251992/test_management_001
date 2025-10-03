from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from backend.apps.projects.models import Environment, Project
from backend.apps.suites.models import Schedule, Suite
from backend.apps.testcases.models import Dataset, TestCase


class RunQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.is_superuser:
            return self
        return self.filter(project__organization__memberships__user=user).distinct()


class Run(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_PASSED = "passed"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_PASSED, "Passed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    project = models.ForeignKey(Project, related_name="runs", on_delete=models.CASCADE)
    suite = models.ForeignKey(Suite, related_name="runs", null=True, blank=True, on_delete=models.SET_NULL)
    environment = models.ForeignKey(Environment, related_name="runs", on_delete=models.SET_NULL, null=True)
    dataset = models.ForeignKey(Dataset, related_name="runs", on_delete=models.SET_NULL, null=True, blank=True)
    triggered_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    total_duration = models.FloatField(null=True, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    schedule = models.ForeignKey(Schedule, null=True, blank=True, on_delete=models.SET_NULL)

    objects = RunQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def mark_started(self) -> None:
        self.status = self.STATUS_RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])

    def mark_completed(self, status: str, summary: dict | None = None) -> None:
        self.status = status
        self.finished_at = timezone.now()
        if self.started_at and self.finished_at:
            self.total_duration = (self.finished_at - self.started_at).total_seconds()
        if summary:
            self.summary = summary
        self.save(update_fields=["status", "finished_at", "total_duration", "summary"])


class RunStep(models.Model):
    run = models.ForeignKey(Run, related_name="steps", on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, related_name="run_steps", on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    log = models.TextField(blank=True)
    screenshot = models.FileField(upload_to="screenshots/", blank=True)
    video = models.FileField(upload_to="videos/", blank=True)

    class Meta:
        ordering = ["order"]


class RunArtifact(models.Model):
    run = models.ForeignKey(Run, related_name="artifacts", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="artifacts/")
    artifact_type = models.CharField(max_length=50, default="file")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]


class RunLog(models.Model):
    run = models.ForeignKey(Run, related_name="logs", on_delete=models.CASCADE)
    level = models.CharField(max_length=20, default="info")
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]


class WebhookDelivery(models.Model):
    run = models.ForeignKey(Run, related_name="webhooks", on_delete=models.CASCADE)
    url = models.URLField()
    payload = models.JSONField(default=dict, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    retries = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-delivered_at", "-id"]
