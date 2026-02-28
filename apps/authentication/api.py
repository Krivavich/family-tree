from django.contrib.auth import get_user_model
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import TwoFactorCode


class TokenObtainWith2FAView(TokenObtainPairView):
    """Step 1: username/password -> issue 2FA challenge code (demo: returned in response)."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        username = request.data.get("username")
        user = get_user_model().objects.filter(username=username).first()
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        challenge = TwoFactorCode.issue_for_user(user)
        return Response(
            {
                "requires_2fa": True,
                "challenge_code": challenge.code,
                "message": "Use /api/auth/2fa/verify/ to finalize login",
            },
            status=status.HTTP_200_OK,
        )


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
