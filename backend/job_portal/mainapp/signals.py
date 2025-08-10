from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SiteUser, ParsedResumeData
from .utils.resume_parser import parse_resume  
from mainapp.utils.resume_parser import parse_resume
import os

@receiver(post_save, sender=SiteUser)
def parse_resume_on_upload(sender, instance, created, **kwargs):
    if instance.resume_link:
        resume_path = instance.resume_link.path
        full_text = parse_resume(resume_path)

        keywords = ["Python", "React", "Django", "AWS", "Machine Learning", "JavaScript"]
        skills = [word for word in keywords if word.lower() in full_text.lower()]

        ParsedResumeData.objects.update_or_create(
            user=instance,
            defaults={
                'full_text': full_text,
                'skills': ", ".join(skills),
            }
        )
