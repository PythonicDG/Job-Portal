from django.contrib import admin
from .models import Menu, SubMenu, CompanyInfo

class SubMenuInline(admin.TabularInline):
    model = SubMenu
    extra = 1  
    ordering = ['order']

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order')
    ordering = ('order',)
    inlines = [SubMenuInline]

@admin.register(SubMenu)
class SubMenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'url', 'order', 'is_active')
    list_filter = ('menu', 'is_active')
    ordering = ('menu', 'order')


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'website')
    search_fields = ('name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
