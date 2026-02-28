from rest_framework import permissions

from .models import TreeMembership


class IsTreeMember(permissions.BasePermission):
    """Allow access only to users that are members of the target tree."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        tree_id = request.data.get("tree") or request.query_params.get("tree")
        if view.action == "create" and tree_id:
            return TreeMembership.objects.filter(tree_id=tree_id, user=request.user).exists()

        return True

    def has_object_permission(self, request, view, obj):
        return TreeMembership.objects.filter(tree=obj.tree, user=request.user).exists()


class HasTreeWriteRole(permissions.BasePermission):
    """Viewer can read, editor/owner can write."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        tree_id = request.data.get("tree") or request.query_params.get("tree")
        if not tree_id:
            return True

        return TreeMembership.objects.filter(
            tree_id=tree_id,
            user=request.user,
            role__in=[TreeMembership.Role.OWNER, TreeMembership.Role.EDITOR],
        ).exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return TreeMembership.objects.filter(
            tree=obj.tree,
            user=request.user,
            role__in=[TreeMembership.Role.OWNER, TreeMembership.Role.EDITOR],
        ).exists()


class HasTreeOwnerRole(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return TreeMembership.objects.filter(tree=obj.tree, user=request.user, role=TreeMembership.Role.OWNER).exists()
