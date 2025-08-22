from django.urls import path
from .views import DashboardConfigAPIView

urlpatterns = [
    path("employer_config/", DashboardConfigAPIView.as_view(), name="dashboard-config"),
]
