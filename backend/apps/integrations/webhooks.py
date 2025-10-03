from __future__ import annotations

import logging
from typing import Any

import requests
from django.urls import reverse

logger = logging.getLogger(__name__)


class WebhookClient:
    def __init__(self, project):
        self.project = project

    def targets(self) -> list[str]:
        return self.project.metadata.get("webhook_urls", []) if hasattr(self.project, "metadata") else []

    def notify_run(self, run):
        payload: dict[str, Any] = {
            "id": run.id,
            "status": run.status,
            "suite": run.suite.slug if run.suite else None,
            "summary": run.summary,
        }
        for target in self.targets():
            try:
                response = requests.post(target, json=payload, timeout=5)
                logger.info("Webhook %s responded with %s", target, response.status_code)
            except Exception:  # pragma: no cover
                logger.exception("Failed to deliver webhook for run %s", run.id)
