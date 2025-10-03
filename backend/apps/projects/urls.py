from __future__ import annotations

from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("projects/", views.project_list, name="list"),
    path("projects/create/", views.project_create, name="create"),
    path("<slug:org_slug>/<slug:project_slug>/", views.project_detail, name="detail"),
    path(
        "<slug:org_slug>/<slug:project_slug>/environments/<slug:env_slug>/",
        views.environment_edit,
        name="environment-edit",
    ),
    path(
        "<slug:org_slug>/<slug:project_slug>/environments/new/",
        views.environment_edit,
        name="environment-create",
    ),
]
