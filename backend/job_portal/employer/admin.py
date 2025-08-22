from django.contrib import admin
from .models import DashboardHeader, HeaderButton, SidebarItem


class HeaderButtonInline(admin.TabularInline):
    model = HeaderButton
    extra = 1
    fields = ("label", "icon", "action")


@admin.register(DashboardHeader)
class DashboardHeaderAdmin(admin.ModelAdmin):
    list_display = ("title", "logo")
    search_fields = ("title",)
    inlines = [HeaderButtonInline]


@admin.register(SidebarItem)
class SidebarItemAdmin(admin.ModelAdmin):
    list_display = ("title", "path", "icon", "order")
    list_editable = ("order",)
    search_fields = ("title", "path")
    ordering = ("order",)
