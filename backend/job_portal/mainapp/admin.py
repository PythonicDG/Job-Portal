from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteUser,
    UserAddress,
    VerifyEmailOtp,
    ExpiringToken,
    ResetPasswordOtp,
    ParsedResumeData,
    Education,
    Experience,
    Skill,
    Certification,
    Language,
    Project
)


class UserAddressInline(admin.TabularInline):
    model = UserAddress
    extra = 0
    fields = ('type', 'address', 'city', 'state', 'country', 'pincode', 'is_selected', 'is_active')
    readonly_fields = ()
    show_change_link = True

class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    show_change_link = True

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0
    show_change_link = True

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0
    show_change_link = True

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    show_change_link = True

class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0
    show_change_link = True

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    fields = ('title', 'technologies', 'start_date', 'end_date', 'is_ongoing', 'project_url', 'repo_url')
    show_change_link = True


@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'user_full_name', 'phone_number',
        'profile_picture_preview', 'created_at'
    )
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)
    inlines = [
        UserAddressInline,
        EducationInline,
        ExperienceInline,
        SkillInline,
        CertificationInline,
        LanguageInline,
        ProjectInline
    ]

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
    list_display = ('user_email', 'type', 'address', 'city', 'state', 'country', 'pincode', 'is_selected', 'is_active')
    search_fields = ('user__user__email', 'address', 'city', 'state', 'country')
    list_filter = ('type', 'is_selected', 'is_active', 'country', 'state')

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

admin.site.register(ParsedResumeData)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'degree', 'field_of_study', 'institution', 'start_year', 'end_year', 'grade')
    search_fields = ('user__user__email', 'degree', 'field_of_study', 'institution')
    list_filter = ('start_year', 'end_year', 'institution')

    def user_email(self, obj):
        return obj.user.user.email
    user_email.admin_order_field = 'user__user__email'
    user_email.short_description = 'User Email'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'job_title', 'company_name', 'start_date', 'end_date', 'is_current')
    search_fields = ('user__user__email', 'job_title', 'company_name')
    list_filter = ('is_current', 'start_date', 'end_date', 'company_name')

    def user_email(self, obj):
        return obj.user.user.email
    user_email.admin_order_field = 'user__user__email'
    user_email.short_description = 'User Email'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'name', 'proficiency')
    search_fields = ('user__user__email', 'name')
    list_filter = ('proficiency',)

    def user_email(self, obj):
        return obj.user.user.email
    user_email.admin_order_field = 'user__user__email'
    user_email.short_description = 'User Email'


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'name', 'issuer', 'date_obtained')
    search_fields = ('user__user__email', 'name', 'issuer')
    list_filter = ('date_obtained',)

    def user_email(self, obj):
        return obj.user.user.email
    user_email.admin_order_field = 'user__user__email'
    user_email.short_description = 'User Email'


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'name', 'proficiency')
    search_fields = ('user__user__email', 'name')
    list_filter = ('proficiency',)

    def user_email(self, obj):
        return obj.user.user.email
    user_email.admin_order_field = 'user__user__email'
    user_email.short_description = 'User Email'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'title', 'technologies', 'start_date', 'end_date', 'is_ongoing', 'project_link_preview')
    search_fields = ('user__user__email', 'title', 'technologies')
    list_filter = ('is_ongoing', 'start_date', 'end_date')

    def user_email(self, obj):
        return obj.user.user.email
    user_email.admin_order_field = 'user__user__email'
    user_email.short_description = 'User Email'

    def project_link_preview(self, obj):
        if obj.project_url:
            return format_html('<a href="{}" target="_blank">Live Link</a>', obj.project_url)
        elif obj.repo_url:
            return format_html('<a href="{}" target="_blank">Repo Link</a>', obj.repo_url)
        return "-"
    project_link_preview.short_description = 'Project Link'
