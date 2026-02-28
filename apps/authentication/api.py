from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import TrustedDevice, TwoFactorCode, TwoFactorDevice
from .services.channels import send_2fa_code
from .services.totp import verify_totp


class TokenObtainWith2FASerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)
    device_id = serializers.IntegerField(required=False)
    trusted_device_token = serializers.CharField(required=False, allow_blank=True)


class TokenObtainWith2FAView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    def post(self, request):
        serializer = TokenObtainWith2FASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        ip_address = request.META.get("REMOTE_ADDR", "")
        trusted_token = serializer.validated_data.get("trusted_device_token")
        if TrustedDevice.validate(user=user, raw_token=trusted_token, user_agent=user_agent, ip_address=ip_address):
            refresh = RefreshToken.for_user(user)
            return Response({"access": str(refresh.access_token), "refresh": str(refresh), "used_trusted_device": True})

        device = self._select_device(user, serializer.validated_data.get("device_id"))
        if not device:
            return Response({"detail": "No verified 2FA device configured"}, status=status.HTTP_400_BAD_REQUEST)

        ratelimit_key = f"2fa-issue:{user.id}"
        if cache.get(ratelimit_key):
            return Response({"detail": "Please wait before requesting another 2FA code"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.set(ratelimit_key, True, timeout=60)

        payload = {
            "requires_2fa": True,
            "device_id": device.id,
            "device_kind": device.kind,
            "message": "Use /api/auth/2fa/verify/ to finalize login",
        }

        if device.kind == TwoFactorDevice.Kind.TOTP:
            return Response(payload, status=status.HTTP_200_OK)

        challenge, raw_code = TwoFactorCode.issue_for_device(user=user, device=device)
        send_2fa_code(device_kind=device.kind, target=device.target, code=raw_code)
        payload["challenge_id"] = challenge.id
        if settings.DEBUG:
            payload["debug_challenge_code"] = raw_code

        return Response(payload, status=status.HTTP_200_OK)

    @staticmethod
    def _select_device(user, device_id):
        devices = TwoFactorDevice.objects.filter(user=user, is_verified=True)
        if device_id:
            return devices.filter(id=device_id).first()
        return devices.order_by("-is_default", "id").first()


class TwoFactorVerifySerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField(max_length=12)
    device_id = serializers.IntegerField(required=False)
    challenge_id = serializers.IntegerField(required=False)
    trust_this_device = serializers.BooleanField(required=False, default=False)


class TwoFactorVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_2fa_verify"

    def post(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_user_model().objects.filter(username=serializer.validated_data["username"]).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        device = TokenObtainWith2FAView._select_device(user, serializer.validated_data.get("device_id"))
        if not device:
            return Response({"detail": "No verified 2FA device configured"}, status=status.HTTP_400_BAD_REQUEST)

        if device.kind == TwoFactorDevice.Kind.TOTP:
            if not device.totp_secret or not verify_totp(device.totp_secret, serializer.validated_data["code"]):
                return Response({"detail": "Invalid or expired 2FA code"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            challenge_id = serializer.validated_data.get("challenge_id")
            if not challenge_id:
                return Response({"detail": "challenge_id is required for non-TOTP verification"}, status=status.HTTP_400_BAD_REQUEST)
            code = TwoFactorCode.objects.filter(
                id=challenge_id,
                user=user,
                device=device,
                is_used=False,
            ).first()
            if not code or not code.is_valid(serializer.validated_data["code"]):
                return Response({"detail": "Invalid or expired 2FA code"}, status=status.HTTP_400_BAD_REQUEST)
            code.is_used = True
            code.save(update_fields=["is_used"])

        refresh = RefreshToken.for_user(user)
        payload = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        if serializer.validated_data.get("trust_this_device"):
            record, raw_token = TrustedDevice.issue_for_user(
                user=user,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                ip_address=request.META.get("REMOTE_ADDR", ""),
            )
            payload["trusted_device_token"] = raw_token
            payload["trusted_device_expires_at"] = record.expires_at

        return Response(payload)


class TokenRefreshPublicView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)
