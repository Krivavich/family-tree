from datetime import timedelta
import hashlib
import hmac
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class TwoFactorCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="two_factor_codes")
    code_hash = models.CharField(max_length=128)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def _hash_code(raw_code: str) -> str:
        key = settings.SECRET_KEY.encode("utf-8")
        return hmac.new(key, raw_code.encode("utf-8"), hashlib.sha256).hexdigest()

    @classmethod
    def issue_for_user(cls, user):
        raw_code = f"{secrets.randbelow(10**6):06d}"
        challenge = cls.objects.create(
            user=user,
            code_hash=cls._hash_code(raw_code),
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        return challenge, raw_code

    def is_valid(self, raw_code: str) -> bool:
        if self.is_used or self.expires_at <= timezone.now():
            return False
        submitted_hash = self._hash_code(raw_code)
        return hmac.compare_digest(self.code_hash, submitted_hash)
