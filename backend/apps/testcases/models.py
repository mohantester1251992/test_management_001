from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from backend.apps.projects.models import Locator, Project


class TestCaseQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self
        return self.filter(project__organization__memberships__user=user).distinct()


class TestCase(models.Model):
    project = models.ForeignKey(Project, related_name="test_cases", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    estimated_duration = models.PositiveIntegerField(default=60, help_text="Estimated duration in seconds")

    objects = TestCaseQuerySet.as_manager()

    class Meta:
        unique_together = ("project", "slug")
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clone(self, user) -> "TestCase":
        clone = TestCase.objects.create(
            project=self.project,
            name=f"{self.name} Copy",
            description=self.description,
            created_by=user,
        )
        for step in self.steps.all():
            TestStep.objects.create(
                test_case=clone,
                order=step.order,
                action=step.action,
                locator=step.locator,
                parameters=step.parameters,
                assertion=step.assertion,
            )
        return clone


class ReusableStep(models.Model):
    project = models.ForeignKey(Project, related_name="reusable_steps", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    action = models.CharField(max_length=50)
    parameters = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Dataset(models.Model):
    project = models.ForeignKey(Project, related_name="datasets", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    data = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("project", "slug")
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class TestStep(models.Model):
    ACTION_CHOICES = [
        ("navigate", "Navigate"),
        ("click", "Click"),
        ("fill", "Fill"),
        ("assert", "Assert"),
        ("wait", "Wait"),
        ("screenshot", "Screenshot"),
    ]

    test_case = models.ForeignKey(TestCase, related_name="steps", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    locator = models.ForeignKey(Locator, null=True, blank=True, on_delete=models.SET_NULL)
    parameters = models.JSONField(default=dict, blank=True)
    assertion = models.JSONField(default=dict, blank=True)
    reusable_step = models.ForeignKey(ReusableStep, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.test_case.name} :: {self.action}"


class AssertionResult(models.Model):
    step = models.ForeignKey(TestStep, related_name="results", on_delete=models.CASCADE)
    run = models.ForeignKey("runner.Run", related_name="assertion_results", on_delete=models.CASCADE)
    passed = models.BooleanField(default=False)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    test_case = models.ForeignKey(TestCase, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    mentions = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Comment by {self.author}"
