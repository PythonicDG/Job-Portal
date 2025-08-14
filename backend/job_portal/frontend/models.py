from django.db import models
from headerfooter.models import SubMenu


class PageSection(models.Model):
    SECTION_TYPE_CHOICES = [
        ("banner", "Banner"),
        ("hero", "Hero"),
        ("contact_us", "Contact US"),
        ("about_us", "About US"), 
        ("testimonial", "Testimonial"),
        ("other", "Other"),
    ]
    submenu = models.ForeignKey(SubMenu, related_name = 'page_sections', on_delete = models.CASCADE)
    section_type = models.CharField(max_length=50, choices=SECTION_TYPE_CHOICES)
    heading = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    slogan = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to='section_logos/', null=True, blank=True)
    logo_alt_text = models.CharField(max_length=255, null=True, blank=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    button_url = models.CharField(max_length=255, null=True, blank=True)
    background_image = models.ImageField(upload_to='section_backgrounds/', null=True, blank=True)
    background_image_alt_text = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='section_images/', null=True, blank=True)
    image_alt_text = models.CharField(max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.section_type} - {self.heading or 'No Heading'}"


class SectionContent(models.Model):
    section = models.ForeignKey(PageSection, related_name="contents", on_delete=models.CASCADE)
    title = models.CharField(null = True, blank = True)
    description = models.CharField(null = True, blank = True)
    icon = models.ImageField(upload_to = "product/", max_length = 255,  null=True, blank=True)
    icon_alternate_text = models.CharField(null = True, blank = True)
    button_text = models.CharField(null = True, blank = True)
    button_url = models.CharField(null = True, blank = True)

    is_active = models.BooleanField(default = True)
    sequence = models.PositiveIntegerField()

    def __str__(self):
        return self.title or self.section.section_type

    def clean(self):
        if self.icon and not self.icon_alternate_text:
            raise ValidationError({
                "icon_alternate_text": "Icon Alternate Text is not Provided"
            })
    

class ContactUs(models.Model):
    email = models.CharField(max_length = 100)
    name = models.CharField(max_length = 100)
    message = models.TextField(max_length = 500)

    def _str_(self):
        return self.email

class FAQSection(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class FAQCategory(models.Model):
    section = models.ForeignKey(FAQSection, on_delete=models.CASCADE, related_name='categories')
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.section.title} - {self.title}"


class FAQQuestion(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question