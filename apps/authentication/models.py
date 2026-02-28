from datetime import timedelta
import hashlib
import hmac
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class TwoFactorDevice(models.Model):
    class Kind(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        TOTP = "totp", "TOTP"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="two_factor_devices")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    label = models.CharField(max_length=120, blank=True)
    target = models.CharField(max_length=255, blank=True)
    totp_secret = models.CharField(max_length=128, blank=True)
    is_verified = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "id"]


class TwoFactorCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="two_factor_codes")
    device = models.ForeignKey(TwoFactorDevice, on_delete=models.CASCADE, related_name="codes", null=True, blank=True)
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
    def issue_for_device(cls, user, device):
        raw_code = f"{secrets.randbelow(10**6):06d}"
        challenge = cls.objects.create(
            user=user,
            device=device,
            code_hash=cls._hash_code(raw_code),
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        return challenge, raw_code

    def is_valid(self, raw_code: str) -> bool:
        if self.is_used or self.expires_at <= timezone.now():
            return False
        submitted_hash = self._hash_code(raw_code)
        return hmac.compare_digest(self.code_hash, submitted_hash)


class TrustedDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trusted_devices")
    token_hash = models.CharField(max_length=128, unique=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.CharField(max_length=64, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def _hash_token(raw_token: str) -> str:
        key = settings.SECRET_KEY.encode("utf-8")
        return hmac.new(key, raw_token.encode("utf-8"), hashlib.sha256).hexdigest()

    @classmethod
    def issue_for_user(cls, user, user_agent: str = "", ip_address: str = ""):
        raw_token = secrets.token_urlsafe(32)
        record = cls.objects.create(
            user=user,
            token_hash=cls._hash_token(raw_token),
            user_agent=user_agent[:255],
            ip_address=ip_address[:64],
            expires_at=timezone.now() + timedelta(days=30),
        )
        return record, raw_token

    @classmethod
    def validate(cls, user, raw_token: str) -> bool:
        if not raw_token:
            return False
        token_hash = cls._hash_token(raw_token)
        device = cls.objects.filter(user=user, token_hash=token_hash).first()
        return bool(device and device.expires_at > timezone.now())
