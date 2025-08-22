from rest_framework import serializers
from .models import DashboardHeader, HeaderButton, SidebarItem


class HeaderButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeaderButton
        fields = ["label", "icon", "action"]


class DashboardHeaderSerializer(serializers.ModelSerializer):
    buttons = HeaderButtonSerializer(many=True, read_only=True)

    class Meta:
        model = DashboardHeader
        fields = ["title", "logo", "buttons"]


class SidebarItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SidebarItem
        fields = ["title", "icon", "path", "order"]
