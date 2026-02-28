from django.contrib import admin

from .models import Fact, FactVersion, MediaAsset, Person, Relationship, Tree, TreeMembership


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    search_fields = ("name", "owner__username")


@admin.register(TreeMembership)
class TreeMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "tree", "user", "role")
    list_filter = ("role",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "tree", "privacy")
    list_filter = ("privacy", "tree")
    search_fields = ("first_name", "last_name")


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ("id", "tree", "from_person", "relation_type", "to_person")
    list_filter = ("relation_type",)


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "person", "uploaded_by", "uploaded_at")


@admin.register(Fact)
class FactAdmin(admin.ModelAdmin):
    list_display = ("id", "person", "key", "confidence", "updated_at")
    search_fields = ("key", "person__first_name", "person__last_name")


@admin.register(FactVersion)
class FactVersionAdmin(admin.ModelAdmin):
    list_display = ("id", "fact", "key", "confidence", "created_at")
