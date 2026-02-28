from django.urls import path

from .api import TokenObtainWith2FAView, TokenRefreshPublicView, TwoFactorVerifyView

urlpatterns = [
    path("token/", TokenObtainWith2FAView.as_view(), name="token-obtain-2fa"),
    path("token/refresh/", TokenRefreshPublicView.as_view(), name="token-refresh"),
    path("2fa/verify/", TwoFactorVerifyView.as_view(), name="2fa-verify"),
]
