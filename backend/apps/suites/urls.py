from __future__ import annotations

from django.urls import path

from . import views

app_name = "suites"

urlpatterns = [
    path("<slug:org_slug>/<slug:project_slug>/suites/", views.suite_list, name="list"),
    path("<slug:org_slug>/<slug:project_slug>/suites/new/", views.suite_create, name="create"),
    path("<slug:org_slug>/<slug:project_slug>/suites/<slug:suite_slug>/", views.suite_detail, name="detail"),
    path(
        "<slug:org_slug>/<slug:project_slug>/suites/<slug:suite_slug>/tests/add/",
        views.suite_add_test,
        name="add-test",
    ),
    path(
        "<slug:org_slug>/<slug:project_slug>/suites/<slug:suite_slug>/schedules/new/",
        views.schedule_create,
        name="schedule-create",
    ),
]
