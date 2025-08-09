from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteUser,
    VerifyEmailOtp,
    UserAddress,
    ExpiringToken,
    ResetPasswordOtp
)


@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'user_full_name', 'phone_number',
        'profile_picture_preview', 'created_at'
    )
    search_fields = (
        'user__email', 'user__first_name',
        'user__last_name', 'phone_number'
    )
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)

    def user_email(self, obj):
        return obj.user.email
    user_email.admin_order_field = 'user__email'
    user_email.short_description = 'Email'

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    user_full_name.short_description = 'Full Name'

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius:4px;" />',
                obj.profile_picture.url
            )
        return "-"
    profile_picture_preview.short_description = 'Profile Picture'


@admin.register(VerifyEmailOtp)
class VerifyEmailOtpAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'is_verified', 'created_at', 'expires_at')
    search_fields = ('email', 'otp')
    list_filter = ('is_verified', 'created_at', 'expires_at')
    readonly_fields = ('created_at',)


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'type', 'address', 'city', 'state',
        'country', 'pincode', 'is_selected', 'is_active'
    )
    search_fields = (
        'user__user__email', 'address', 'city', 'state', 'country'
    )
    list_filter = (
        'type', 'is_selected', 'is_active', 'country', 'state'
    )

    def user_email(self, obj):
        return obj.user.user.email
    user_email.admin_order_field = 'user__user__email'
    user_email.short_description = 'User Email'


@admin.register(ExpiringToken)
class ExpiringTokenAdmin(admin.ModelAdmin):
    list_display = ('expires_at', 'is_expired_display')
    list_filter = ('expires_at',)

    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.boolean = True
    is_expired_display.short_description = 'Expired?'


@admin.register(ResetPasswordOtp)
class ResetPasswordOtpAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'otp', 'is_verified', 'created_at')
    search_fields = ('user__user__email', 'otp')
    list_filter = ('is_verified', 'created_at')

    def user_email(self, obj):
        return obj.user.user.email
    user_email.short_description = 'User Email'
