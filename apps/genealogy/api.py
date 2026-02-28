from rest_framework import permissions, serializers, viewsets

from .models import Person, Relationship


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "tree", "first_name", "last_name", "birth_date", "death_date", "biography", "privacy"]


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = ["id", "tree", "from_person", "to_person", "relation_type"]


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects.select_related("tree")
    permission_classes = [permissions.IsAuthenticated]


class RelationshipViewSet(viewsets.ModelViewSet):
    serializer_class = RelationshipSerializer
    queryset = Relationship.objects.select_related("tree", "from_person", "to_person")
    permission_classes = [permissions.IsAuthenticated]
