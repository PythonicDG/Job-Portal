from django.dispatch import Signal, receiver
from .models import Notification, SiteUser

job_created = Signal() 

@receiver(job_created)
def create_job_notification(sender, job_instance, **kwargs):
    for user in SiteUser.objects.all():
        Notification.objects.create(
            user=user,
            title=f"New Job: {job_instance.title}",
            message=f"A new {job_instance.title} role has been posted at {job_instance.employer.name}."
        )
