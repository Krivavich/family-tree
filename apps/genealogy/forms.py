from django import forms
from django.db import transaction

from .models import Event, Person, Relationship, Tree, TreeMembership


def editable_trees_for_user(user):
    return Tree.objects.filter(
        memberships__user=user,
        memberships__role__in=[TreeMembership.Role.OWNER, TreeMembership.Role.EDITOR],
    ).distinct()


def editable_trees_with_default_for_user(user):
    """Return editable trees and bootstrap a personal tree for a new user.

    If user has no memberships at all, create a personal tree and owner membership
    so required dropdowns in create forms are never empty for first-time owners.
    """
    trees = editable_trees_for_user(user)
    if trees.exists() or TreeMembership.objects.filter(user=user).exists():
        return trees

    with transaction.atomic():
        tree = Tree.objects.create(name=f"Древо семьи {user.username}", owner=user)
        TreeMembership.objects.create(tree=tree, user=user, role=TreeMembership.Role.OWNER)
    return editable_trees_for_user(user)


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["tree", "first_name", "last_name", "birth_date", "death_date", "biography", "privacy"]
        labels = {
            "tree": "Древо",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "birth_date": "Дата рождения",
            "death_date": "Дата смерти",
            "biography": "Биография",
            "privacy": "Приватность",
        }
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date", "placeholder": "Дата"}),
            "death_date": forms.DateInput(attrs={"type": "date", "placeholder": "Дата"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["tree"].queryset = editable_trees_with_default_for_user(user)


class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ["tree", "from_person", "to_person", "relation_type"]
        labels = {
            "tree": "Древо",
            "from_person": "От кого",
            "to_person": "Кому",
            "relation_type": "Тип связи",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            trees = editable_trees_with_default_for_user(user)
            self.fields["tree"].queryset = trees
            self.fields["from_person"].queryset = Person.objects.filter(tree__in=trees)
            self.fields["to_person"].queryset = Person.objects.filter(tree__in=trees)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["person", "event_type", "event_date", "place", "description", "source_reference"]
        labels = {
            "person": "Персона",
            "event_type": "Тип события",
            "event_date": "Дата",
            "place": "Место",
            "description": "Описание",
            "source_reference": "Источник",
        }
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date", "placeholder": "Дата"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["person"].queryset = Person.objects.filter(tree__in=editable_trees_with_default_for_user(user)).distinct()
