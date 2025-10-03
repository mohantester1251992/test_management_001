from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SlackNotifier:
    def __init__(self, project):
        self.project = project

    def webhook_url(self) -> str | None:
        return self.project.metadata.get("slack_webhook") if hasattr(self.project, "metadata") else None

    def notify_run(self, run):
        url = self.webhook_url()
        if not url:
            return
        payload = {
            "text": f"Run {run.id} for suite {run.suite.name if run.suite else 'Ad-hoc'} finished with {run.status}"
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception:  # pragma: no cover
            logger.exception("Failed to post to Slack for run %s", run.id)
