from django.urls import path
from . import views

urlpatterns = [
    path("send_otp_for_register_email/", views.send_otp_for_register_email),
    path("verify_otp_email_verification/", views.verify_otp_email_verification),
    path("user_registration/", views.user_registration),
    path("user_login/", views.user_login)

]
