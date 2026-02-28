from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Tree(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_trees")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self) -> str:
        return self.name


class TreeMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        EDITOR = "editor", "Editor"
        VIEWER = "viewer", "Viewer"

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tree_memberships")
    role = models.CharField(max_length=16, choices=Role.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tree", "user"], name="unique_tree_membership"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.tree_id}:{self.role}"


class Person(models.Model):
    class Privacy(models.TextChoices):
        PUBLIC = "public", "Public"
        FAMILY = "family", "Family"
        PRIVATE = "private", "Private"

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="persons")
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)
    privacy = models.CharField(max_length=16, choices=Privacy.choices, default=Privacy.FAMILY)

    class Meta:
        ordering = ["last_name", "first_name", "id"]

    def clean(self) -> None:
        if self.birth_date and self.death_date and self.death_date < self.birth_date:
            raise ValidationError({"death_date": "Дата смерти не может быть раньше даты рождения."})

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Relationship(models.Model):
    class Type(models.TextChoices):
        PARENT = "parent", "Parent"
        SPOUSE = "spouse", "Spouse"

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="relationships")
    from_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="outgoing_relationships")
    to_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="incoming_relationships")
    relation_type = models.CharField(max_length=20, choices=Type.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(from_person=models.F("to_person")), name="no_self_relationship"),
            models.UniqueConstraint(
                fields=["tree", "from_person", "to_person", "relation_type"],
                name="unique_relationship_in_tree",
            ),
        ]

    def clean(self) -> None:
        if self.from_person_id and self.to_person_id:
            if self.from_person.tree_id != self.tree_id or self.to_person.tree_id != self.tree_id:
                raise ValidationError("Оба человека в связи должны принадлежать тому же дереву.")

    def __str__(self) -> str:
        return f"{self.from_person} -> {self.relation_type} -> {self.to_person}"


class MediaAsset(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="media_assets")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="media_assets/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]


class Fact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="facts")
    key = models.CharField(max_length=120)
    value = models.TextField()
    confidence = models.CharField(max_length=1, choices=(("A", "Document"), ("B", "Witness"), ("C", "Family lore")), default="C")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["person", "key"], name="unique_fact_key_per_person"),
        ]

    def __str__(self) -> str:
        return f"{self.person_id}:{self.key}"


class FactVersion(models.Model):
    fact = models.ForeignKey(Fact, on_delete=models.CASCADE, related_name="versions")
    key = models.CharField(max_length=120)
    value = models.TextField()
    confidence = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
