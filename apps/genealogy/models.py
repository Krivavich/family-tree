from django.conf import settings
from django.db import models


class Tree(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_trees")
    created_at = models.DateTimeField(auto_now_add=True)

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
        unique_together = ("tree", "user")


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


class MediaAsset(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="media_assets")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="media_assets/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Fact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="facts")
    key = models.CharField(max_length=120)
    value = models.TextField()
    confidence = models.CharField(max_length=1, choices=(("A", "Document"), ("B", "Witness"), ("C", "Family lore")), default="C")
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        FactVersion.objects.create(fact=self, key=self.key, value=self.value, confidence=self.confidence)


class FactVersion(models.Model):
    fact = models.ForeignKey(Fact, on_delete=models.CASCADE, related_name="versions")
    key = models.CharField(max_length=120)
    value = models.TextField()
    confidence = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
