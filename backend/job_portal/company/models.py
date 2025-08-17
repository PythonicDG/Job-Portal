from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=600)
    google_place_id = models.CharField(max_length=600, unique=True, null=True, blank=True)
    website = models.URLField(max_length=600, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    industry = models.CharField(max_length=600, null=True, blank=True)
    sector = models.CharField(max_length=600, null=True, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    founded_by = models.CharField(max_length=600, null=True, blank=True)
    revenue = models.CharField(max_length=600, null=True, blank=True)
    mission = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone_number = models.CharField(max_length=600, null=True, blank=True)
    international_phone_number = models.CharField(max_length=600, null=True, blank=True)
    google_rating = models.FloatField(null=True, blank=True)
    total_google_reviews = models.IntegerField(null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)
    open_now = models.BooleanField(null=True, blank=True)
    types = models.JSONField(null=True, blank=True)
    fsq_id = models.CharField(max_length=600, null=True, blank=True)
    fsq_categories = models.JSONField(null=True, blank=True)
    fsq_popularity = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CompanyPhoto(models.Model):
    company = models.ForeignKey(Company, related_name="photos", on_delete=models.CASCADE)
    photo_url = models.URLField()
    source = models.CharField(max_length=50, default="google")
    created_at = models.DateTimeField(auto_now_add=True)


class EmployeeReview(models.Model):
    company = models.ForeignKey(Company, related_name="employee_reviews", on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=600)
    rating = models.FloatField()
    title = models.CharField(max_length=600, null=True, blank=True)
    review = models.TextField()
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
