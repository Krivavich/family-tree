from django import forms

from .models import Person, Relationship, Tree


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["tree", "first_name", "last_name", "birth_date", "death_date", "biography", "privacy"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields["tree"].queryset = Tree.objects.filter(memberships__user=user).distinct()


class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ["tree", "from_person", "to_person", "relation_type"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            trees = Tree.objects.filter(memberships__user=user).distinct()
            self.fields["tree"].queryset = trees
            self.fields["from_person"].queryset = Person.objects.filter(tree__in=trees)
            self.fields["to_person"].queryset = Person.objects.filter(tree__in=trees)
