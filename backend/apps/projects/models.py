from __future__ import annotations

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from backend.apps.organizations.models import Organization
from .encryption import decrypt, encrypt, mask_secret


class ProjectQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self
        return self.filter(organization__memberships__user=user).distinct()


class Project(models.Model):
    organization = models.ForeignKey(Organization, related_name="projects", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    default_base_url = models.URLField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects_created")
    created_at = models.DateTimeField(default=timezone.now)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        unique_together = ("organization", "slug")
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def active_environments(self):
        return self.environments.filter(is_active=True)


class Environment(models.Model):
    project = models.ForeignKey(Project, related_name="environments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    base_url = models.URLField()
    variables = models.JSONField(default=dict, blank=True)
    secrets = models.ManyToManyField("Secret", blank=True, related_name="environments")
    is_active = models.BooleanField(default=True)
    concurrency = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    timezone = models.CharField(max_length=64, default="UTC")

    class Meta:
        unique_together = ("project", "slug")
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.project.name}::{self.name}"


class Secret(models.Model):
    KEY_TYPES = [
        ("api_key", "API Key"),
        ("password", "Password"),
        ("token", "Token"),
        ("custom", "Custom"),
    ]

    project = models.ForeignKey(Project, related_name="secrets", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    encrypted_value = models.TextField()
    key_type = models.CharField(max_length=32, choices=KEY_TYPES, default="custom")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ["name"]

    def set_value(self, value: str) -> None:
        self.encrypted_value = encrypt(value)

    def get_value(self) -> str:
        return decrypt(self.encrypted_value)

    def masked_value(self) -> str:
        return mask_secret(self.get_value())


class Locator(models.Model):
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    ROLE = "role"

    STRATEGY_CHOICES = [
        (CSS, "CSS"),
        (XPATH, "XPath"),
        (TEXT, "Text"),
        (ROLE, "Role"),
    ]

    project = models.ForeignKey(Project, related_name="locators", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    strategy = models.CharField(max_length=20, choices=STRATEGY_CHOICES, default=CSS)
    value = models.TextField()
    description = models.TextField(blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    health_status = models.CharField(max_length=20, default="unknown")

    class Meta:
        unique_together = ("project", "name")
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def mark_checked(self, status: str) -> None:
        self.health_status = status
        self.last_checked_at = timezone.now()
        self.save(update_fields=["health_status", "last_checked_at"])
