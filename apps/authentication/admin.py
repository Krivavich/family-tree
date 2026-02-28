from django.contrib import admin

from .models import TwoFactorCode


@admin.register(TwoFactorCode)
class TwoFactorCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "code", "is_used", "expires_at", "created_at")
    list_filter = ("is_used",)
    search_fields = ("user__username",)
