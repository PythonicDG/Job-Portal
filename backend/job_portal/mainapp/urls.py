from django.urls import path
from .views import CustomerRegistration
from .views import CustomerRegistration, APIRootView


urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('register/', CustomerRegistration.as_view(), name='customer-register'),
]
