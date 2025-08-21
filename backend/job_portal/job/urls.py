from django.urls import path
from . import views

urlpatterns = [
    path('trigger_job_fetch/', views.sync_jobs, name='job-list'),
    path('jobs/', views.jobs_list, name='jobs-list'),
    path('sidebar_menu_list/', views.sidebar_menu_list, name='jobs-list'),
    path('save_jobs/', views.save_jobs, name='save-jobs'),
    path('unsave_job/<str:job_id>/', views.unsave_job),
    path('view_job/', views.view_job),
    path('recent_viewed_jobs/', views.recent_viewed_jobs),
    path('dashboard_data/', views.dashboard_data),
    path('profile_button_items/', views.profile_button_items),
    path('saved_jobs/', views.user_saved_jobs),
    path('list_notifications/', views.list_notifications)

]
