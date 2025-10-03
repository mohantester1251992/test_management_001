from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class OrganizationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self
        return self.filter(memberships__user=user)


class Organization(models.Model):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("team", "Team"),
        ("enterprise", "Enterprise"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    plan = models.CharField(max_length=32, choices=PLAN_CHOICES, default="team")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizations_created")
    created_at = models.DateTimeField(default=timezone.now)

    objects = OrganizationQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def member_count(self) -> int:
        return self.memberships.count()


class Membership(models.Model):
    ROLE_OWNER = "owner"
    ROLE_MAINTAINER = "maintainer"
    ROLE_VIEWER = "viewer"

    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_MAINTAINER, "Maintainer"),
        (ROLE_VIEWER, "Viewer"),
    ]

    organization = models.ForeignKey(Organization, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="memberships", on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("organization", "user")
        ordering = ["organization", "user"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} @ {self.organization}"

    def can_manage(self) -> bool:
        return self.role in {self.ROLE_OWNER, self.ROLE_MAINTAINER}
