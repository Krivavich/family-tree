from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("genealogy", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="mediaasset",
            name="preview_file",
            field=models.FileField(blank=True, upload_to="media_previews/"),
        ),
        migrations.CreateModel(
            name="ProposedChange",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("target_model", models.CharField(max_length=64)),
                ("target_id", models.PositiveIntegerField()),
                ("change_payload", models.JSONField(default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "proposer",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="proposed_changes", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "reviewer",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_proposed_changes", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "tree",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="proposed_changes", to="genealogy.tree"),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
