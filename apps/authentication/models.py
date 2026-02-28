from datetime import timedelta
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class TwoFactorCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="two_factor_codes")
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def issue_for_user(cls, user):
        code = f"{secrets.randbelow(10**6):06d}"
        return cls.objects.create(user=user, code=code, expires_at=timezone.now() + timedelta(minutes=10))

    def is_valid(self, raw_code: str) -> bool:
        return (not self.is_used) and self.expires_at > timezone.now() and self.code == raw_code
