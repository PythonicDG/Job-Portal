from django.urls import path
from . import views

urlpatterns = [
    path("send_otp_for_register_email/", views.send_otp_for_register_email),
    path("verify_otp_email_verification/", views.verify_otp_email_verification),
    path("user_registration/", views.user_registration),
    path("user_login/", views.user_login),
    path("user_logout/", views.user_logout),
    path("get_user_profile/", views.get_user_profile),
    path("delete_user_profile/", views.delete_user_profile),
    path("send_otp_forgot_password/", views.send_otp_forgot_password),
    path("verify_forgot_password_otp/", views.verify_forgot_password_otp),
    path("update_password/", views.update_password)
]
