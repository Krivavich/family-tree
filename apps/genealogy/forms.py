from django import forms

from .models import Person, Relationship


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["tree", "first_name", "last_name", "birth_date", "death_date", "biography", "privacy"]


class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ["tree", "from_person", "to_person", "relation_type"]
