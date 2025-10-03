from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from backend.apps.projects.models import Project
from backend.apps.runner.models import Run


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    projects = Project.objects.for_user(request.user)[:6]
    recent_runs = Run.objects.visible_to(request.user).select_related("suite", "environment")[:10]
    context = {
        "projects": projects,
        "recent_runs": recent_runs,
    }
    return render(request, "dashboard.html", context)


def toggle_theme(request: HttpRequest) -> HttpResponse:
    theme = request.POST.get("theme")
    if request.user.is_authenticated:
        request.user.theme_preference = theme
        request.user.save(update_fields=["theme_preference"])
    else:
        request.session["theme"] = theme
    return redirect(request.META.get("HTTP_REFERER", "/"))
