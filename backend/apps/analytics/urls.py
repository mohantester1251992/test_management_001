from __future__ import annotations

from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("<slug:org_slug>/<slug:project_slug>/analytics/", views.project_analytics, name="project"),
]
