from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.accounts"

    def ready(self) -> None:  # pragma: no cover
        from auditlog.registry import auditlog

        from . import models

        auditlog.register(models.User)
