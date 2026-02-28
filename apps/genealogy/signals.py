from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Fact, FactVersion


@receiver(post_save, sender=Fact)
def create_fact_version(sender, instance: Fact, created: bool, **kwargs) -> None:
    latest = instance.versions.first()
    if latest and latest.key == instance.key and latest.value == instance.value and latest.confidence == instance.confidence:
        return

    FactVersion.objects.create(
        fact=instance,
        key=instance.key,
        value=instance.value,
        confidence=instance.confidence,
    )
