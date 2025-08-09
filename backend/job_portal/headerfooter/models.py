from django.db import models


class CompanyInfo(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Info"
        verbose_name_plural = "Company Info"

    def __str__(self):
        return self.name


class Menu(models.Model):
    title = models.CharField(max_length=100, unique=True)
    url = models.CharField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of the menu item")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class SubMenu(models.Model):
    menu = models.ForeignKey(Menu, related_name='submenus', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    url = models.CharField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of the submenu item")

    class Meta:
        ordering = ['order']
        unique_together = ('menu', 'title')

    def __str__(self):
        return f"{self.menu.title} -> {self.title}"
