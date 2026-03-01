from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TrustedDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token_hash", models.CharField(max_length=128, unique=True)),
                ("user_agent", models.CharField(blank=True, max_length=255)),
                ("ip_address", models.CharField(blank=True, max_length=64)),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_used_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trusted_devices", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="TwoFactorDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("email", "Email"), ("sms", "SMS"), ("totp", "TOTP")], max_length=16)),
                ("label", models.CharField(blank=True, max_length=120)),
                ("target", models.CharField(blank=True, max_length=255)),
                ("totp_secret", models.CharField(blank=True, max_length=128)),
                ("is_verified", models.BooleanField(default=False)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="two_factor_devices", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-is_default", "id"]},
        ),
        migrations.AddField(
            model_name="twofactorcode",
            name="device",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="codes", to="authentication.twofactordevice"),
        ),
    ]
