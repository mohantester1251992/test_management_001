from __future__ import annotations

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("theme-toggle/", views.toggle_theme, name="theme-toggle"),
]
