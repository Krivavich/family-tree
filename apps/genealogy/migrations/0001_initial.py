from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tree",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "owner",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owned_trees", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["name", "id"]},
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=120)),
                ("last_name", models.CharField(blank=True, max_length=120)),
                ("birth_date", models.DateField(blank=True, null=True)),
                ("death_date", models.DateField(blank=True, null=True)),
                ("biography", models.TextField(blank=True)),
                ("privacy", models.CharField(choices=[("public", "Public"), ("family", "Family"), ("private", "Private")], default="family", max_length=16)),
                ("tree", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="persons", to="genealogy.tree")),
            ],
            options={"ordering": ["last_name", "first_name", "id"]},
        ),
        migrations.CreateModel(
            name="Fact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=120)),
                ("value", models.TextField()),
                ("confidence", models.CharField(choices=[("A", "Document"), ("B", "Witness"), ("C", "Family lore")], default="C", max_length=1)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("person", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="facts", to="genealogy.person")),
            ],
        ),
        migrations.CreateModel(
            name="FactVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=120)),
                ("value", models.TextField()),
                ("confidence", models.CharField(max_length=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("fact", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="versions", to="genealogy.fact")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="MediaAsset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("file", models.FileField(upload_to="media_assets/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("person", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="media_assets", to="genealogy.person")),
                (
                    "uploaded_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
        migrations.CreateModel(
            name="Relationship",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("relation_type", models.CharField(choices=[("parent", "Parent"), ("spouse", "Spouse")], max_length=20)),
                ("from_person", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="outgoing_relationships", to="genealogy.person")),
                ("to_person", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="incoming_relationships", to="genealogy.person")),
                ("tree", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="relationships", to="genealogy.tree")),
            ],
        ),
        migrations.CreateModel(
            name="TreeMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("owner", "Owner"), ("editor", "Editor"), ("viewer", "Viewer")], max_length=16)),
                ("tree", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="genealogy.tree")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tree_memberships", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="treemembership",
            constraint=models.UniqueConstraint(fields=("tree", "user"), name="unique_tree_membership"),
        ),
        migrations.AddConstraint(
            model_name="relationship",
            constraint=models.CheckConstraint(check=models.Q(("from_person", models.F("to_person")), _negated=True), name="no_self_relationship"),
        ),
        migrations.AddConstraint(
            model_name="relationship",
            constraint=models.UniqueConstraint(fields=("tree", "from_person", "to_person", "relation_type"), name="unique_relationship_in_tree"),
        ),
        migrations.AddConstraint(
            model_name="fact",
            constraint=models.UniqueConstraint(fields=("person", "key"), name="unique_fact_key_per_person"),
        ),
    ]
