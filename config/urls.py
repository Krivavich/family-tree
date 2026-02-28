from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from apps.genealogy.api import PersonViewSet, RelationshipViewSet

router = DefaultRouter()
router.register("persons", PersonViewSet, basename="person")
router.register("relationships", RelationshipViewSet, basename="relationship")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("apps.genealogy.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", get_schema_view(title="Family Tree API", version="1.1.0"), name="openapi-schema"),
]
