from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.genealogy.models import Fact, Person, Relationship

from .context import get_current_user
from .models import AuditLog


def _log(instance, action: str) -> None:
    actor = get_current_user()
    AuditLog.objects.create(
        actor=actor,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        payload={"repr": str(instance)},
    )


@receiver(post_save, sender=Person)
def person_saved(sender, instance: Person, created: bool, **kwargs) -> None:
    _log(instance, "created" if created else "updated")


@receiver(post_delete, sender=Person)
def person_deleted(sender, instance: Person, **kwargs) -> None:
    _log(instance, "deleted")


@receiver(post_save, sender=Relationship)
def relationship_saved(sender, instance: Relationship, created: bool, **kwargs) -> None:
    _log(instance, "created" if created else "updated")


@receiver(post_delete, sender=Relationship)
def relationship_deleted(sender, instance: Relationship, **kwargs) -> None:
    _log(instance, "deleted")


@receiver(post_save, sender=Fact)
def fact_saved(sender, instance: Fact, created: bool, **kwargs) -> None:
    _log(instance, "created" if created else "updated")
