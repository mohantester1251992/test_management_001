from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from backend.apps.projects.models import Project
from backend.apps.testcases.models import TestCase

from .forms import ScheduleForm, SuiteForm
from .models import Schedule, Suite, SuiteTestCase


@login_required
def suite_list(request: HttpRequest, org_slug: str, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    suites = project.suites.all()
    return render(request, "suites/list.html", {"project": project, "suites": suites})


@login_required
def suite_detail(request: HttpRequest, org_slug: str, project_slug: str, suite_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    suite = get_object_or_404(Suite, project=project, slug=suite_slug)
    tests = project.test_cases.all()
    schedule_form = ScheduleForm(initial={"suite": suite})
    return render(
        request,
        "suites/detail.html",
        {
            "project": project,
            "suite": suite,
            "tests": tests,
            "schedule_form": schedule_form,
        },
    )


@login_required
def suite_create(request: HttpRequest, org_slug: str, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    if request.method == "POST":
        form = SuiteForm(request.POST, project=project)
        if form.is_valid():
            suite = form.save(commit=False)
            suite.project = project
            suite.created_by = request.user
            suite.save()
            form.save_m2m()
            messages.success(request, "Suite created")
            return redirect(reverse("suites:detail", args=[org_slug, project_slug, suite.slug]))
    else:
        form = SuiteForm(project=project)
    return render(request, "suites/form.html", {"project": project, "form": form})


@login_required
def suite_add_test(request: HttpRequest, org_slug: str, project_slug: str, suite_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    suite = get_object_or_404(Suite, project=project, slug=suite_slug)
    test_id = request.POST.get("test_case")
    if test_id:
        test_case = get_object_or_404(TestCase, id=test_id, project=project)
        SuiteTestCase.objects.get_or_create(suite=suite, test_case=test_case)
        messages.success(request, "Test added to suite")
    return redirect(reverse("suites:detail", args=[org_slug, project_slug, suite_slug]))


@login_required
def schedule_create(request: HttpRequest, org_slug: str, project_slug: str, suite_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    suite = get_object_or_404(Suite, project=project, slug=suite_slug)
    form = ScheduleForm(request.POST)
    if form.is_valid():
        schedule = form.save(commit=False)
        schedule.suite = suite
        schedule.save()
        messages.success(request, "Schedule saved")
    return redirect(reverse("suites:detail", args=[org_slug, project_slug, suite_slug]))
