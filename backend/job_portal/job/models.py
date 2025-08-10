from django.db import models


class Employer(models.Model):
    name = models.CharField(max_length = 500)
    employer_logo =  models.ImageField(upload_to = "employer_logo/")
    website = models.URLField(blank=True, null=True, max_length = 500)

    class Meta:
        unique_together = ('name', 'website')
    

class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('city', 'state', 'country')

class Job(models.Model):
    job_id = models.CharField(max_length = 500, unique=True)  
    title = models.CharField(max_length = 500)
    description = models.TextField(null = True, blank = True)
    is_remote = models.BooleanField(default = False)
    employment_type = models.CharField(max_length = 50, blank = True, null = True)
    posted_at = models.DateTimeField(null = True, blank = True)
    posted_timestamp = models.BigIntegerField(null = True, blank = True)
    google_link = models.URLField(blank = True, null = True, max_length = 500)

    min_salary = models.FloatField(blank = True, null = True)
    max_salary = models.FloatField(blank = True, null = True)
    salary_period = models.CharField(max_length = 50, blank = True, null = True)

    employer = models.ForeignKey(Employer, on_delete = models.CASCADE)
    location = models.ForeignKey(Location, on_delete = models.SET_NULL, null = True, blank = True)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now =  True)


class ApplyOption(models.Model):
    job = models.ForeignKey(Job, related_name='apply_options', on_delete=models.CASCADE)
    publisher = models.CharField(max_length=500, null = True, blank = True)
    apply_link = models.URLField(max_length = 500, null = True, blank = True)
    is_direct = models.BooleanField(default=False)


class EmploymentType(models.Model):
    job = models.ForeignKey(Job, related_name='employment_types', on_delete=models.CASCADE)
    type = models.CharField(max_length=50, null = True, blank = True)

class SidebarMenu(models.Model):
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    icon = models.ImageField(upload_to='sidebar_icons/')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title