from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path("fetch_records/", views.fetch_records),
    path("contact_us/", views.contact_us),
    path("faq_list/", views.faq_list)
    
]
