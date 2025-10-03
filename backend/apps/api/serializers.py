from __future__ import annotations

from rest_framework import serializers

from backend.apps.projects.models import Environment, Project
from backend.apps.runner.models import Run
from backend.apps.suites.models import Schedule, Suite
from backend.apps.testcases.models import Dataset, TestCase


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = ["id", "name", "slug", "base_url", "is_active", "concurrency", "timezone", "variables"]


class ProjectSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Project._meta.get_field("organization").remote_field.model.objects.all())
    environments = EnvironmentSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "organization",
            "name",
            "slug",
            "description",
            "default_base_url",
            "tags",
            "environments",
        ]


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["id", "name", "slug", "description", "data"]


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "tags",
            "estimated_duration",
            "is_active",
        ]


class SuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suite
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "retries",
            "parallelism",
            "tags",
        ]


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = [
            "id",
            "status",
            "created_at",
            "started_at",
            "finished_at",
            "total_duration",
            "summary",
        ]
