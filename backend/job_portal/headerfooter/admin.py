from django.contrib import admin
from .models import (Menu, SubMenu, CompanyInfo,     Footer,
    ContactInfo,
    FooterMenu,
    FooterMenuItem,
    SocialLink,
    LegalLink,)

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

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'background_color', 'text_color', 'border_color')
    search_fields = ('company_name',)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'address')
    search_fields = ('email', 'phone')


class FooterMenuItemInline(admin.TabularInline):
    model = FooterMenuItem
    extra = 1


@admin.register(FooterMenu)
class FooterMenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'footer')
    inlines = [FooterMenuItemInline]


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'link')
    search_fields = ('name',)


@admin.register(LegalLink)
class LegalLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    search_fields = ('name',)