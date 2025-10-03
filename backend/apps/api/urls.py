from __future__ import annotations

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("projects", views.ProjectViewSet, basename="project")
router.register("tests", views.TestCaseViewSet, basename="testcase")
router.register("suites", views.SuiteViewSet, basename="suite")
router.register("runs", views.RunViewSet, basename="run")

urlpatterns = router.urls
