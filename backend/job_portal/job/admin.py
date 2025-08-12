from django.contrib import admin
from .models import Employer, Location, Job, ApplyOption, EmploymentType, SidebarMenu, UserSavedJob, user_viewed_jobs, user_applied_jobs_log

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country')
    search_fields = ('city', 'state', 'country')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'posted_at', 'is_remote')
    search_fields = ('title', 'description')
    list_filter = ('is_remote', 'employment_type')

@admin.register(ApplyOption)
class ApplyOptionAdmin(admin.ModelAdmin):
    list_display = ('job', 'publisher', 'is_direct')
    search_fields = ('publisher',)

@admin.register(EmploymentType)
class EmploymentTypeAdmin(admin.ModelAdmin):
    list_display = ('job', 'type')
    search_fields = ('type',)


@admin.register(SidebarMenu)
class SidebarMenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')
    search_fields = ('title',)

@admin.register(UserSavedJob)
class UserSavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'job__title')

@admin.register(user_viewed_jobs)
class UserViewedJobsAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'viewed_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'job__title')

@admin.register(user_applied_jobs_log)
class UserAppliedJobsAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'applied_at')
    list_filter = ('user',)
    search_fields = ('user__username', 'job__title')