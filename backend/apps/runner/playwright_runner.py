from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils import timezone

from backend.apps.projects.models import Environment
from backend.apps.testcases.models import TestCase

try:  # pragma: no cover - optional dependency
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover
    sync_playwright = None


ARTIFACT_ROOT = Path(settings.MEDIA_ROOT) / "artifacts"
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)


def execute_test_case(test_case: TestCase, environment: Environment) -> dict[str, Any]:
    """Execute a single test case using Playwright.

    In this reference implementation we simulate execution when Playwright is not
    available, enabling local development without browsers. When Playwright is
    installed the real browser workflow is used.
    """

    if sync_playwright is None:
        return {
            "status": "passed",
            "message": f"Simulated run for {test_case.name}",
            "steps": [
                {"order": step.order, "action": step.action, "status": "passed"}
                for step in test_case.steps.all()
            ],
        }

    with sync_playwright() as p:  # pragma: no cover - requires browser
        browser = p.chromium.launch(headless=True, channel=settings.PLAYWRIGHT_CHANNEL)
        page = browser.new_page(base_url=environment.base_url)
        results: list[dict[str, Any]] = []
        status = "passed"
        for step in test_case.steps.order_by("order"):
            step_result = {"order": step.order, "action": step.action, "status": "passed"}
            try:
                if step.action == "navigate":
                    page.goto(step.parameters.get("url", environment.base_url))
                elif step.action == "click" and step.locator:
                    page.click(step.locator.value)
                elif step.action == "fill" and step.locator:
                    page.fill(step.locator.value, step.parameters.get("value", ""))
                elif step.action == "wait":
                    page.wait_for_timeout(int(step.parameters.get("timeout", 1000)))
                elif step.action == "assert":
                    page.wait_for_selector(step.locator.value)
                elif step.action == "screenshot":
                    path = ARTIFACT_ROOT / f"{timezone.now().timestamp()}-{test_case.slug}.png"
                    page.screenshot(path=path)
                    step_result["screenshot"] = str(path.relative_to(settings.MEDIA_ROOT))
                else:
                    page.wait_for_timeout(100)
            except Exception as exc:  # pragma: no cover
                step_result["status"] = "failed"
                step_result["error"] = str(exc)
                status = "failed"
            results.append(step_result)
        browser.close()
        return {
            "status": status,
            "message": f"Run for {test_case.name} completed with {status}",
            "steps": results,
        }
