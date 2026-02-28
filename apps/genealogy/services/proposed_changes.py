from django.db import transaction
from django.utils import timezone

from apps.genealogy.models import Person, ProposedChange


def apply_proposed_change(change: ProposedChange, reviewer) -> ProposedChange:
    if change.status != ProposedChange.Status.PENDING:
        return change

    with transaction.atomic():
        locked = ProposedChange.objects.select_for_update().get(id=change.id)
        if locked.status != ProposedChange.Status.PENDING:
            return locked

        if locked.target_model == "person":
            person = Person.objects.select_for_update().filter(id=locked.target_id, tree=locked.tree).first()
            if person:
                allowed = {"first_name", "last_name", "birth_date", "death_date", "biography", "privacy"}
                for field, value in locked.change_payload.items():
                    if field in allowed:
                        setattr(person, field, value)
                person.save()

        locked.status = ProposedChange.Status.APPROVED
        locked.reviewer = reviewer
        locked.reviewed_at = timezone.now()
        locked.save(update_fields=["status", "reviewer", "reviewed_at"])
        return locked


def reject_proposed_change(change: ProposedChange, reviewer) -> ProposedChange:
    if change.status != ProposedChange.Status.PENDING:
        return change

    with transaction.atomic():
        locked = ProposedChange.objects.select_for_update().get(id=change.id)
        if locked.status != ProposedChange.Status.PENDING:
            return locked
        locked.status = ProposedChange.Status.REJECTED
        locked.reviewer = reviewer
        locked.reviewed_at = timezone.now()
        locked.save(update_fields=["status", "reviewer", "reviewed_at"])
        return locked
