
from django.dispatch import Signal, receiver
from .models import Notification, SiteUser


jobs_synced = Signal()

@receiver(jobs_synced)
def create_jobs_notification(sender, total_jobs, **kwargs):
    if total_jobs > 0:
        for user in SiteUser.objects.all():
            Notification.objects.create(
                user=user,
                title="Jobs Synced",
                message=f"{total_jobs} new jobs were added successfully."
            )
