from django.db import models

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
