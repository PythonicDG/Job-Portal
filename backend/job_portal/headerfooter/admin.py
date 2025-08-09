from django.contrib import admin
from .models import Menu, SubMenu

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
    list_display = ('title', 'menu', 'url', 'order')
    list_filter = ('menu',)
    ordering = ('menu', 'order')
