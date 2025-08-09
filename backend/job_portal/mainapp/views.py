from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import *
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

    
@api_view(["POST"])
def send_otp_for_register_email(request):
    try:
        email = request.data.get("email")

        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        mail_status = send_otp_mail(email)

        if mail_status == 0:
            return Response({"message": "Something went wrong sending the email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_otp_email_verification(request):
    try:
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email:
            return JsonResponse({"error": "please enter email"})
        
        if not otp:
            return JsonResponse({"error":"please enter otp"})

        otp_instance = VerifyEmailOtp.objects.filter(email = email, otp = otp).first()

        if not otp_instance:
            return JsonResponse({"error": "please enter valid otp"})

        if timezone.now() > otp_instance.expires_at:
            return JsonResponse({"error": "OTP expired"})

        otp_instance.is_verified = True
        
        otp_instance.save()

        return JsonResponse({"message": "OTP verified Success"})
    
    except Exception as e:
        return JsonResponse({"error": str(r)})
    
@api_view(["POST"])
def user_registration(request):
    with transaction.atomic():
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            otp = request.data.get("otp")
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            phone_number = request.data.get("phone_number")
            profile_picture = request.FILES.get("profile_picture")
            address = request.data.get("address")
            city = request.data.get("city")
            state = request.data.get("state")
            country = request.data.get("country")
            pincode = request.data.get("pincode")
            resume_link = request.FILES.get("resume_link")
            is_selected = request.data.get('is_selected', False)

            if not all((email, first_name, last_name, phone_number, address, city, state, country, pincode)):
                return JsonResponse({"error": "Invalid request data"}, status=400)
            
            otp_instance = VerifyEmailOtp.objects.filter(email=email, otp=otp).first()

            if not otp_instance:
                return JsonResponse({"error": "Invalid OTP"}, status=400)

            if timezone.now() > otp_instance.expires_at:
                return JsonResponse({"error": "OTP Expired"}, status=400)
            
            existing_user = SiteUser.objects.filter(user__email=email).first()  

            if existing_user:
                return JsonResponse({"error": "User with this Email already exists"}, status=400)
            
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            site_user = SiteUser.objects.create(
                user=user,
                phone_number=phone_number,
                profile_picture=profile_picture,
                resume_link=resume_link
            )
            
            UserAddress.objects.create(
                user=site_user,
                address=address,
                city=city,
                state=state,
                country=country,
                pincode=pincode
            )
            
            otp_instance.delete()
            # send_registration_mail(user)
            return JsonResponse({"message": "User registered successfully"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
        
@api_view(['POST'])
def user_login(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status = status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username = email, password = password)

        if user is not None:
            token, crated = Token.objects.get_or_create(user = user)

            return JsonResponse({"message": "Login sucess",
                                 "token": token.key,
                                 "user": {
                                     "id": user.id,
                                     "email": user.email,
                                 }})
            
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        return JsonResponse({"error": str(e)})
    
@api_view(["POST"])
def send_otp_forgot_password(request):
    try:
        email = request.data.get("email")
        
        if not email:
            return JsonResponse({"message": "email is requierd"})
        
        user_instance = User.objects.filter(email = email, is_staff = False).first()

        if not user_instance:
            return JsonResponse({"error": "User not found"}, status = status.HTTP_400_BAD_REQUEST)

        if user_instance.is_active == False:
            return JsonResponse({"message": "User is not Active"})
        
        first_name = user_instance.first_name
        
        mail_status = send_forgot_password_otp(email, first_name)

        return JsonResponse({"message": "OTP sent Successfull"})
        
    except Exception as e:
        return JsonResponse({"error": str(e)})

@api_view(['POST'])
def verify_forgot_password_otp(request):
    try:
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email:
            return JsonResponse({"error": "email required"})
        
        if not otp:
            return JsonResponse({"error": "otp required"})
        
        otp_instance = VerifyEmailOtp.objects.filter(
            email = email, otp = otp
        ).first()

        if not otp_instance:
            return JsonResponse({"error": "otp not found or invalid"})
        
        if otp_instance.expires_at < timezone.now():
            return JsonResponse({"message": "Invalid OTP"})
        
        otp_instance.is_verified = True
        
        otp_instance.save()

        return JsonResponse({"message": "verification success"})

    except Exception as e:
        return JsonResponse({"message":str(e)})