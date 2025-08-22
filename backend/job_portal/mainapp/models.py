from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, FileExtensionValidator, ValidationError
from datetime import timedelta

class ExpiringToken(models.Model):
    expires_at = models.DateTimeField(blank = True, null = True)

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + timedelta(hours = 1)
        
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at
    

def validate_file_size(file):
    max_size_mb = 5
    if file.size > max_size_mb * 1024 *1024:
        raise ValidationError(f"File size should not exceed {max_size_mb}MB.")

def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user.id}_{filename}"


class SiteUser(models.Model):
    USER_ROLES = (
        ("employee", "Employee"),
        ("employer", "Employer"),
    )
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default="employee")
    profile_picture = models.ImageField(upload_to = 'profile_pictures/')
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Enter a valid phone number (e.g. +12345678901)"
    )
    resume_link = models.FileField(upload_to = resume_upload_path, 
                validators = [
                    FileExtensionValidator(allowed_extensions = ["pdf", "doc", "docx"]),
                    validate_file_size
                ], 
                help_text = "Upload a resume (PDF, DOC OR DOCX). Max size 5MB."
    )
    
    date_of_birth = models.DateTimeField(blank = True, null = True)
    gender = models.CharField(max_length=10, choices=(("Male", "male"), ("Female", "female"), ("Other", "other")), blank=True)
    linkdin_url = models.CharField(max_length=255, blank=True, null=True)
    github_url = models.CharField(max_length=255, blank=True, null=True)
    portfolio_url = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now_add = True)
    
    def profile_completion(self):
        score = 0
        
        if self.profile_picture and self.phone_number and self.gender and self.date_of_birth:
            score += 15
            
        if self.resume_link:
            score += 10

        if self.education.exists():
            score += 15

        if self.experience.exists():
            score += 15

        if self.skills.exists():
            score += 10

        if self.projects.exists():
            score += 10

        if self.certifications.exists():
            score += 5

        if self.languages.exists():
            score += 5

        if self.user_address.exists():
            score += 5

        if hasattr(self, "preferences") and (
            self.preferences.preferred_job_roles or self.preferences.preferred_locations
        ):
            score += 10

        return min(score, 100)
    def __str__(self):
        return f"Profile of {self.user.username}"

class Employer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employer_profile"
    )

    company_name = models.CharField(max_length=200)
    company_phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format: '+999999999'."
            )
        ],
    )
    company_website = models.URLField(blank=True, null=True)
    industry_type = models.CharField(max_length=100, blank=True, null=True)
    company_size = models.CharField(
        max_length=50,
        choices=(
            ("1-10", "1-10 employees"),
            ("11-50", "11-50 employees"),
            ("51-200", "51-200 employees"),
            ("201-500", "201-500 employees"),
            ("500+", "500+ employees"),
        ),
        blank=True,
        null=True,
    )
    company_logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    pan_gst = models.CharField(max_length=30, blank=True, null=True)

    brc_file = models.FileField(upload_to="brc_documents/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class EmployerAddress(models.Model):
    employer = models.OneToOneField(
        Employer, on_delete=models.CASCADE, related_name="address"
    )
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country}"


    
class VerifyEmailOtp(models.Model):
    email = models.EmailField(unique = True)
    otp = models.CharField(unique = True)
    created_at = models.DateTimeField(auto_now = True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default = False)

    def __str__(self):
        return self.email
    
class UserAddress(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE, related_name="user_address")
    type = models.CharField(max_length=50, choices=(
        ("Permanent Address", "permanent address"),
        ("Current Address", "current address")
    ), null = True, blank = True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=100)
    is_selected = models.BooleanField(default=False)
    is_active = models.BooleanField(default = True, null = True, blank = True)

    def __str__(self):
        return f"{self.type} - {self.address}"
    
class ResetPasswordOtp(models.Model):
    user = models.ForeignKey(SiteUser, on_delete = models.DO_NOTHING)
    otp = models.CharField(max_length = 6)
    created_at = models.DateTimeField()
    is_verified = models.BooleanField(default = False)
    

class ParsedResumeData(models.Model):
    user = models.OneToOneField(SiteUser, on_delete=models.CASCADE)
    full_text = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    matched_keywords = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Education(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE, related_name="education")
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=150)
    start_year = models.DateField()
    end_year = models.DateField(blank=True, null=True)
    grade = models.CharField(max_length=20, blank=True, null=True)
    
class Experience(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE, related_name="experience")
    job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
class Skill(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=20, choices=(
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Expert", "Expert"),
    ), default="Beginner")
    
class Certification(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=150)
    issuer = models.CharField(max_length=100, blank=True, null=True)
    date_obtained = models.DateField(blank=True, null=True)

class Language(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE, related_name="languages")
    name = models.CharField(max_length=50)
    proficiency = models.CharField(max_length=20, choices=(
        ("Basic", "Basic"),
        ("Intermediate", "Intermediate"),
        ("Fluent", "Fluent"),
        ("Native", "Native"),
    ))

class Project(models.Model):
    user = models.ForeignKey(
        SiteUser, 
        on_delete=models.CASCADE, 
        related_name="projects"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    technologies = models.CharField(
        max_length=255, 
        help_text="Comma-separated (e.g., Django, React, PostgreSQL)"
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=False)
    project_url = models.URLField(blank=True, null=True, help_text="Live demo or deployed link")
    repo_url = models.URLField(blank=True, null=True, help_text="GitHub/GitLab/Bitbucket link")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.user.username})"


