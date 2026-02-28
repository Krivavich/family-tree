from django.contrib import admin

from .models import TrustedDevice, TwoFactorCode, TwoFactorDevice


@admin.register(TwoFactorDevice)
class TwoFactorDeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "kind", "target", "is_verified", "is_default")
    list_filter = ("kind", "is_verified", "is_default")


@admin.register(TwoFactorCode)
class TwoFactorCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "device", "is_used", "expires_at", "created_at")
    list_filter = ("is_used",)
    search_fields = ("user__username",)


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "ip_address", "expires_at", "last_used_at")
    search_fields = ("user__username", "ip_address")
