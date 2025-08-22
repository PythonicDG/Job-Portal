from django.db import models
from django.contrib.auth.models import User

class DashboardHeader(models.Model):
    title = models.CharField(max_length=100, default="Employer Dashboard")
    logo = models.ImageField(upload_to="dashboard/logos/", blank=True, null=True)

    def __str__(self):
        return self.title


class HeaderButton(models.Model):
    header = models.ForeignKey(
        DashboardHeader, on_delete=models.CASCADE, related_name="buttons"
    )
    label = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, help_text="e.g. lucide icon name or fontawesome class")
    action = models.CharField(max_length=255, help_text="URL or frontend route")

    def __str__(self):
        return f"{self.label} ({self.action})"


class SidebarItem(models.Model):
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="e.g. lucide icon name or fontawesome class")
    path = models.CharField(max_length=255, help_text="Frontend route or URL")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.path})"
