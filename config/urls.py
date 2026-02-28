from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from apps.genealogy.api import PersonViewSet, ProposedChangeViewSet, RelationshipViewSet

router = DefaultRouter()
router.register("persons", PersonViewSet, basename="person")
router.register("relationships", RelationshipViewSet, basename="relationship")
router.register("proposed-changes", ProposedChangeViewSet, basename="proposed-change")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("apps.genealogy.urls")),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", get_schema_view(title="Family Tree API", version="1.3.0"), name="openapi-schema"),
]
