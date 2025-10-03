from __future__ import annotations

from django.urls import path

from . import views

app_name = "testcases"

urlpatterns = [
    path("<slug:org_slug>/<slug:project_slug>/tests/", views.test_list, name="list"),
    path("<slug:org_slug>/<slug:project_slug>/tests/new/", views.test_create, name="create"),
    path("<slug:org_slug>/<slug:project_slug>/tests/<slug:test_slug>/", views.test_detail, name="detail"),
    path(
        "<slug:org_slug>/<slug:project_slug>/tests/<slug:test_slug>/steps/add/",
        views.test_step_add,
        name="step-add",
    ),
    path("<slug:org_slug>/<slug:project_slug>/datasets/", views.dataset_list, name="datasets"),
    path("<slug:org_slug>/<slug:project_slug>/datasets/new/", views.dataset_edit, name="dataset-create"),
    path(
        "<slug:org_slug>/<slug:project_slug>/datasets/<slug:slug>/edit/",
        views.dataset_edit,
        name="dataset-edit",
    ),
]
