from django.contrib import admin
from .models import Employer, Location, Job, ApplyOption, EmploymentType

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
