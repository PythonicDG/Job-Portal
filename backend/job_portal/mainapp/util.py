import os
import random 
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from rest_framework.response import Response
from django.template.loader import render_to_string
from .models import(VerifyEmailOtp,)
from job_portal.settings import *
from threading import Thread

def send_otp_mail(email):
    otp = random.randint(100000, 999999)  

    print("Generated OTP:", otp, "Length:", len(str(otp)))

    expires_at = timezone.now() + timedelta(minutes=5)

    otp_instance, is_created = VerifyEmailOtp.objects.update_or_create(
        email=email,
        defaults={"otp": otp, "expires_at": expires_at, "is_verified": False}
    )

    context = {
        "email": email,
        "otp": otp
    }

    email_body = render_to_string("emails/send_otp_email_template.html", context)

    mail_status = send_mail(
        subject="Verify Your Email",
        message="",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=email_body,
        fail_silently=False,
    )

    return mail_status

def send_otp_mail_threaded(email):
    def run():
        try:
            send_otp_mail(email)
        except Exception as e:
            print(f"Failed to send OTP email to {email}: {e}")

    thread = Thread(target=run)
    thread.start()

def send_registration_mail(user_instance):
    context = {
        "first_name": user_instance.first_name,
        "last_name": user_instance.last_name,
        "email": user_instance.email
    }
    
    email_body = render_to_string("emails/registration_email.html", context)

    mail_status = send_mail(
        subject = "Registration Sucess",
        message = "",
        from_email = EMAIL_HOST_USER,
        recipient_list = [email],
        html_message = email_body,
        fail_silently = False
    )
    
    return mail_status
    
def send_forgot_password_otp(email, first_name):
    
    otp = random.randint(100000, 999999)
    expires_at = timezone.now() + timedelta(minutes=5)

    otp_instance, is_created = VerifyEmailOtp.objects.update_or_create(
        email=email,
        defaults={"otp": otp, "expires_at": expires_at, "is_verified": False}
    )
    
    context = {
        "otp": otp,
        "email": email,
        "first_name": first_name
    }
    
    email_body = render_to_string("emails/send_otp_email_template.html", context)

    mail_status = send_mail(
        subject = "Forgot Password OTP",
            message = "",
        from_email = EMAIL_HOST_USER,
        recipient_list = [email],
        html_message = email_body,
        fail_silently = False
        
    )

    return mail_status

def dipak(database):
    pass

def send_otp_mail_threaded_forgot(email, first_name):
    def run():
        try:
            send_forgot_password_otp(email, first_name)
        except Exception as e:
            print(f"Failed to send OTP email to {email}: {e}")

    thread = Thread(target=run)
    thread.start()