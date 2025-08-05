from django.contrib import admin
from .models import PageSection

@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'heading', 'is_active', 'created_at', 'updated_at')
    list_filter = ('section_type', 'is_active')
    search_fields = ('heading', 'description', 'slogan')
    ordering = ('section_type', '-created_at')
