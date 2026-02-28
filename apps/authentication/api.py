from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import TwoFactorCode


class TokenObtainWith2FASerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class TokenObtainWith2FAView(APIView):
    permission_classes = [permissions.AllowAny]

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

        latest = TwoFactorCode.objects.filter(user=user).order_by("-created_at").first()
        if latest and latest.created_at > timezone.now() - timedelta(seconds=60):
            return Response({"detail": "Please wait before requesting another 2FA code"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        challenge, raw_code = TwoFactorCode.issue_for_user(user)
        payload = {
            "requires_2fa": True,
            "challenge_id": challenge.id,
            "message": "Use /api/auth/2fa/verify/ to finalize login",
        }
        if settings.DEBUG:
            payload["debug_challenge_code"] = raw_code

        return Response(payload, status=status.HTTP_200_OK)


class TwoFactorVerifySerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField(max_length=6)


class TwoFactorVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_user_model().objects.filter(username=serializer.validated_data["username"]).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        code = TwoFactorCode.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if not code or not code.is_valid(serializer.validated_data["code"]):
            return Response({"detail": "Invalid or expired 2FA code"}, status=status.HTTP_400_BAD_REQUEST)

        code.is_used = True
        code.save(update_fields=["is_used"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


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
