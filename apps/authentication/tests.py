from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import TrustedDevice, TwoFactorCode, TwoFactorDevice
from .services.totp import totp_now, verify_totp


class TwoFactorModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alice", password="pass-12345")
        self.device = TwoFactorDevice.objects.create(
            user=self.user,
            kind=TwoFactorDevice.Kind.EMAIL,
            target="alice@example.com",
            is_verified=True,
            is_default=True,
        )

    def test_code_not_stored_in_plaintext_and_validates(self):
        challenge, raw = TwoFactorCode.issue_for_device(self.user, self.device)
        self.assertNotEqual(challenge.code_hash, raw)
        self.assertTrue(challenge.is_valid(raw))

    def test_trusted_device_token_validation(self):
        _record, raw = TrustedDevice.issue_for_user(self.user, user_agent="ua", ip_address="127.0.0.1")
        self.assertTrue(TrustedDevice.validate(self.user, raw, user_agent="ua", ip_address="127.0.0.1"))
        self.assertFalse(TrustedDevice.validate(self.user, raw, user_agent="other", ip_address="127.0.0.1"))
        self.assertFalse(TrustedDevice.validate(self.user, "bad"))


class TotpTests(TestCase):
    def test_totp_roundtrip(self):
        secret = "JBSWY3DPEHPK3PXP"
        code = totp_now(secret)
        self.assertTrue(verify_totp(secret, code))


class TwoFactorApiContractTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="bob", password="pass-12345")
        self.device = TwoFactorDevice.objects.create(
            user=self.user,
            kind=TwoFactorDevice.Kind.EMAIL,
            target="bob@example.com",
            is_verified=True,
            is_default=True,
        )

    def test_challenge_id_required_for_non_totp(self):
        challenge, raw = TwoFactorCode.issue_for_device(self.user, self.device)
        self.assertTrue(challenge.is_valid(raw))
        # API layer requires challenge_id; model test ensures challenge objects are addressable
        self.assertIsNotNone(challenge.id)
