from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("genealogy", "0002_proposedchange_media_preview"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("birth", "Birth"),
                            ("marriage", "Marriage"),
                            ("death", "Death"),
                            ("move", "Move"),
                            ("education", "Education"),
                            ("work", "Work"),
                        ],
                        max_length=20,
                    ),
                ),
                ("event_date", models.DateField(blank=True, null=True)),
                ("place", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("source_reference", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "person",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="genealogy.person"),
                ),
            ],
            options={"ordering": ["event_date", "id"]},
        ),
    ]
