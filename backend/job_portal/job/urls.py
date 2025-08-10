from django.urls import path
from . import views

urlpatterns = [
    path('trigger_job_fetch/', views.sync_jobs, name='job-list'),
    path('jobs/', views.jobs_list, name='jobs-list'),
]
