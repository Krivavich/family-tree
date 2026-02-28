from django.urls import path

from .views import (
    PersonCreateView,
    PersonDeleteView,
    PersonListView,
    PersonUpdateView,
    RelationshipCreateView,
    RelationshipListView,
)

urlpatterns = [
    path("", PersonListView.as_view(), name="person-list"),
    path("persons/new/", PersonCreateView.as_view(), name="person-create"),
    path("persons/<int:pk>/edit/", PersonUpdateView.as_view(), name="person-edit"),
    path("persons/<int:pk>/delete/", PersonDeleteView.as_view(), name="person-delete"),
    path("relationships/", RelationshipListView.as_view(), name="relationship-list"),
    path("relationships/new/", RelationshipCreateView.as_view(), name="relationship-create"),
]
