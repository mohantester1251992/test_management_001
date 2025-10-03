from __future__ import annotations

from django.core.mail import send_mail


class EmailNotifier:
    def __init__(self, project):
        self.project = project

    def recipients(self) -> list[str]:
        return self.project.metadata.get("notification_emails", []) if hasattr(self.project, "metadata") else []

    def notify_run(self, run):
        recipients = self.recipients()
        if not recipients:
            return
        subject = f"Run {run.id} completed"
        message = f"Suite {run.suite.name if run.suite else 'Ad-hoc'} finished with {run.status}"
        send_mail(subject, message, None, recipients)
