from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from backend.apps.organizations.models import Membership

from .forms import EnvironmentForm, ProjectForm
from .models import Environment, Project


def _require_membership(user, project: Project) -> None:
    if user.is_superuser:
        return
    if not Membership.objects.filter(organization=project.organization, user=user).exists():
        raise PermissionDenied


@login_required
def project_list(request: HttpRequest) -> HttpResponse:
    projects = Project.objects.for_user(request.user).select_related("organization")
    context = {"projects": projects}
    return render(request, "projects/list.html", context)


@login_required
def project_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProjectForm(request.user, request.POST)
        if form.is_valid():
            project = form.save()
            return redirect(reverse("projects:detail", args=[project.organization.slug, project.slug]))
    else:
        form = ProjectForm(request.user)
    return render(request, "projects/create.html", {"form": form})


@login_required
def project_detail(request: HttpRequest, org_slug: str, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    _require_membership(request.user, project)
    environments = project.environments.all()
    context = {
        "project": project,
        "environments": environments,
    }
    return render(request, "projects/detail.html", context)


@login_required
def environment_edit(request: HttpRequest, org_slug: str, project_slug: str, env_slug: str | None = None) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    _require_membership(request.user, project)
    environment = None
    if env_slug:
        environment = get_object_or_404(Environment, project=project, slug=env_slug)
    if request.method == "POST":
        form = EnvironmentForm(project, request.POST, instance=environment)
        if form.is_valid():
            env = form.save()
            return redirect(reverse("projects:detail", args=[project.organization.slug, project.slug]))
    else:
        form = EnvironmentForm(project, instance=environment)
    return render(request, "projects/environment_form.html", {"project": project, "form": form})
