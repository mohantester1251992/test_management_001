from __future__ import annotations

from django.http import HttpResponse
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest
from rest_framework import permissions, viewsets

from backend.apps.organizations.models import Membership, Organization
from backend.apps.projects.models import Project
from backend.apps.runner.models import Run
from backend.apps.suites.models import Suite
from backend.apps.testcases.models import TestCase

from .serializers import ProjectSerializer, RunSerializer, SuiteSerializer, TestCaseSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        organization = serializer.validated_data["organization"]
        if not self.request.user.is_superuser and not Membership.objects.filter(
            organization=organization, user=self.request.user
        ).exists():
            raise permissions.PermissionDenied("You do not have access to this organization")
        serializer.save(created_by=self.request.user)


class TestCaseViewSet(viewsets.ModelViewSet):
    serializer_class = TestCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TestCase.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        try:
            project = Project.objects.for_user(self.request.user).get(id=self.request.data.get("project"))
        except Project.DoesNotExist as exc:
            raise permissions.PermissionDenied("Invalid project selection") from exc
        serializer.save(project=project, created_by=self.request.user)


class SuiteViewSet(viewsets.ModelViewSet):
    serializer_class = SuiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Suite.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        try:
            project = Project.objects.for_user(self.request.user).get(id=self.request.data.get("project"))
        except Project.DoesNotExist as exc:
            raise permissions.PermissionDenied("Invalid project selection") from exc
        serializer.save(project=project, created_by=self.request.user)


class RunViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Run.objects.visible_to(self.request.user)


def metrics_view(request):
    output = generate_latest(REGISTRY)
    return HttpResponse(output, content_type=CONTENT_TYPE_LATEST)
