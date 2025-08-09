from rest_framework import serializers
from .models import Menu, SubMenu

class SubMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubMenu
        fields = ['id', 'title', 'url', 'order']

class MenuSerializer(serializers.ModelSerializer):
    submenus = SubMenuSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ['id', 'title', 'url', 'order', 'submenus']
