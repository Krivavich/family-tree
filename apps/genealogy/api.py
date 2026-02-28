from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Person, ProposedChange, Relationship
from .permissions import HasTreeOwnerRole, HasTreeWriteRole, IsTreeMember
from .services.proposed_changes import apply_proposed_change, reject_proposed_change


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "tree", "first_name", "last_name", "birth_date", "death_date", "biography", "privacy"]


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = ["id", "tree", "from_person", "to_person", "relation_type"]


class ProposedChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposedChange
        fields = [
            "id",
            "tree",
            "proposer",
            "target_model",
            "target_id",
            "change_payload",
            "status",
            "reviewer",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = ["proposer", "reviewer", "reviewed_at", "created_at", "status"]


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated, IsTreeMember, HasTreeWriteRole]

    def get_queryset(self):
        return Person.objects.select_related("tree").filter(tree__memberships__user=self.request.user).distinct()


class RelationshipViewSet(viewsets.ModelViewSet):
    serializer_class = RelationshipSerializer
    permission_classes = [permissions.IsAuthenticated, IsTreeMember, HasTreeWriteRole]

    def get_queryset(self):
        return Relationship.objects.select_related("tree", "from_person", "to_person").filter(
            tree__memberships__user=self.request.user
        ).distinct()


class ProposedChangeViewSet(viewsets.ModelViewSet):
    serializer_class = ProposedChangeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTreeMember]

    def get_queryset(self):
        return ProposedChange.objects.select_related("tree", "proposer", "reviewer").filter(
            tree__memberships__user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(proposer=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, HasTreeOwnerRole])
    def approve(self, request, pk=None):
        instance = self.get_object()
        updated = apply_proposed_change(instance, reviewer=request.user)
        return Response(ProposedChangeSerializer(updated).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, HasTreeOwnerRole])
    def reject(self, request, pk=None):
        instance = self.get_object()
        updated = reject_proposed_change(instance, reviewer=request.user)
        return Response(ProposedChangeSerializer(updated).data, status=status.HTTP_200_OK)
