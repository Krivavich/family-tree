from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import PersonForm, RelationshipForm
from .models import Person, Relationship


class PersonListView(LoginRequiredMixin, ListView):
    model = Person
    template_name = "genealogy/person_list.html"

    def get_queryset(self):
        return Person.objects.filter(tree__memberships__user=self.request.user).distinct()


class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "genealogy/person_form.html"
    success_url = reverse_lazy("person-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "genealogy/person_form.html"
    success_url = reverse_lazy("person-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        return Person.objects.filter(tree__memberships__user=self.request.user).distinct()


class PersonDeleteView(LoginRequiredMixin, DeleteView):
    model = Person
    template_name = "genealogy/person_confirm_delete.html"
    success_url = reverse_lazy("person-list")

    def get_queryset(self):
        return Person.objects.filter(tree__memberships__user=self.request.user).distinct()


class RelationshipListView(LoginRequiredMixin, ListView):
    model = Relationship
    template_name = "genealogy/relationship_list.html"

    def get_queryset(self):
        return Relationship.objects.filter(tree__memberships__user=self.request.user).select_related(
            "from_person", "to_person"
        ).distinct()


class RelationshipCreateView(LoginRequiredMixin, CreateView):
    model = Relationship
    form_class = RelationshipForm
    template_name = "genealogy/relationship_form.html"
    success_url = reverse_lazy("relationship-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
