from django.urls import path
from . import views

urlpatterns = [
    path('trigger_job_fetch/', views.sync_jobs, name='job-list'),
    path('jobs/', views.jobs_list, name='jobs-list'),
    path('sidebar_menu_list/', views.sidebar_menu_list, name='jobs-list'),
    path('save_jobs/', views.save_jobs, name='save-jobs'),
]
