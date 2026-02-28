from django import forms

from .models import Event, Person, Relationship, Tree, TreeMembership


def editable_trees_for_user(user):
    return Tree.objects.filter(
        memberships__user=user,
        memberships__role__in=[TreeMembership.Role.OWNER, TreeMembership.Role.EDITOR],
    ).distinct()


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["tree", "first_name", "last_name", "birth_date", "death_date", "biography", "privacy"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["tree"].queryset = editable_trees_for_user(user)


class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ["tree", "from_person", "to_person", "relation_type"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            trees = editable_trees_for_user(user)
            self.fields["tree"].queryset = trees
            self.fields["from_person"].queryset = Person.objects.filter(tree__in=trees)
            self.fields["to_person"].queryset = Person.objects.filter(tree__in=trees)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["person", "event_type", "event_date", "place", "description", "source_reference"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["person"].queryset = Person.objects.filter(tree__in=editable_trees_for_user(user)).distinct()
