from __future__ import annotations

from django.urls import path

from . import views

app_name = "runs"

urlpatterns = [
    path("<slug:org_slug>/<slug:project_slug>/runs/", views.run_list, name="list"),
    path("<slug:org_slug>/<slug:project_slug>/runs/<int:run_id>/", views.run_detail, name="detail"),
]
