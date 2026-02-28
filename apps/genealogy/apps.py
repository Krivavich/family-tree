from django.apps import AppConfig


class GenealogyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.genealogy"

    def ready(self) -> None:
        from . import signals  # noqa: F401
