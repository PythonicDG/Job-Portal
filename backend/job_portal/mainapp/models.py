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
    user = models.OneToOneField(User, on_delete = models.CASCADE)
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
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

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
    