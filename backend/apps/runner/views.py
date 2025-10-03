from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from backend.apps.projects.models import Project

from .models import Run


@login_required
def run_list(request: HttpRequest, org_slug: str, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    runs = Run.objects.visible_to(request.user).filter(project=project)
    paginator = Paginator(runs, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "runs/list.html", {"project": project, "page": page})


@login_required
def run_detail(request: HttpRequest, org_slug: str, project_slug: str, run_id: int) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    run = get_object_or_404(Run.objects.visible_to(request.user), project=project, id=run_id)
    return render(request, "runs/detail.html", {"project": project, "run": run})
