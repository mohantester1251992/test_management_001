from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from backend.apps.projects.models import Project
from backend.apps.runner.models import Run


@login_required
def project_analytics(request: HttpRequest, org_slug: str, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    runs = Run.objects.filter(project=project)
    status_counts = runs.values("status").annotate(total=Count("id"))
    flaky_tests = (
        project.test_cases.filter(run_steps__run__status=Run.STATUS_FAILED)
        .annotate(failure_count=Count("run_steps", filter=Q(run_steps__run__status=Run.STATUS_FAILED)))
        .order_by("-failure_count")[:5]
    )
    context = {
        "project": project,
        "status_counts": status_counts,
        "flaky_tests": flaky_tests,
    }
    return render(request, "analytics/project.html", context)
