from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from backend.apps.projects.models import Project

from .forms import DatasetForm, TestCaseForm, TestStepForm
from .models import Dataset, TestCase, TestStep


@login_required
def test_list(request: HttpRequest, org_slug: str, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    test_cases = project.test_cases.all()
    return render(request, "testcases/list.html", {"project": project, "test_cases": test_cases})


@login_required
def test_detail(request: HttpRequest, org_slug: str, project_slug: str, test_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    test_case = get_object_or_404(TestCase, project=project, slug=test_slug)
    step_form = TestStepForm(project, initial={"order": test_case.steps.count() + 1})
    return render(
        request,
        "testcases/detail.html",
        {"project": project, "test_case": test_case, "step_form": step_form},
    )


@login_required
def test_create(request: HttpRequest, org_slug: str, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    if request.method == "POST":
        form = TestCaseForm(request.POST)
        if form.is_valid():
            test_case = form.save(commit=False)
            test_case.project = project
            test_case.created_by = request.user
            test_case.save()
            messages.success(request, "Test created")
            return redirect(reverse("testcases:detail", args=[org_slug, project_slug, test_case.slug]))
    else:
        form = TestCaseForm()
    return render(request, "testcases/form.html", {"form": form, "project": project})


@login_required
def test_step_add(request: HttpRequest, org_slug: str, project_slug: str, test_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    test_case = get_object_or_404(TestCase, project=project, slug=test_slug)
    form = TestStepForm(project, request.POST)
    if form.is_valid():
        step = form.save(commit=False)
        step.test_case = test_case
        step.save()
        messages.success(request, "Step added")
    return redirect(reverse("testcases:detail", args=[org_slug, project_slug, test_slug]))


@login_required
def dataset_list(request: HttpRequest, org_slug: str, project_slug: str) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    datasets = project.datasets.all()
    return render(request, "testcases/datasets.html", {"project": project, "datasets": datasets})


@login_required
def dataset_edit(request: HttpRequest, org_slug: str, project_slug: str, slug: str | None = None) -> HttpResponse:
    project = get_object_or_404(Project, organization__slug=org_slug, slug=project_slug)
    dataset = None
    if slug:
        dataset = get_object_or_404(Dataset, project=project, slug=slug)
    if request.method == "POST":
        form = DatasetForm(request.POST, instance=dataset)
        if form.is_valid():
            ds = form.save(commit=False)
            ds.project = project
            ds.save()
            messages.success(request, "Dataset saved")
            return redirect(reverse("testcases:datasets", args=[org_slug, project_slug]))
    else:
        form = DatasetForm(instance=dataset)
    return render(request, "testcases/dataset_form.html", {"project": project, "form": form})
