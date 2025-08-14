from django.contrib import admin
from .models import PageSection, SectionContent, ContactUs, FAQSection, FAQCategory, FAQQuestion

@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'heading', 'is_active', 'created_at', 'updated_at')
    list_filter = ('section_type', 'is_active')
    search_fields = ('heading', 'description', 'slogan')
    ordering = ('section_type', '-created_at')

@admin.register(SectionContent)
class SectionContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'is_active', 'sequence')
    ordering = ('section', 'sequence')

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')
    search_fields = ('name', 'email')

class FAQQuestionInline(admin.TabularInline):
    model = FAQQuestion
    extra = 1

class FAQCategoryAdmin(admin.ModelAdmin):
    inlines = [FAQQuestionInline]
    list_display = ('title', 'section')
    list_filter = ('section',)

class FAQSectionAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(FAQSection, FAQSectionAdmin)
admin.site.register(FAQCategory, FAQCategoryAdmin)
admin.site.register(FAQQuestion)