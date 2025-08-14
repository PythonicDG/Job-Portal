from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .util import send_otp_mail, send_otp_mail_threaded, send_forgot_password_otp, send_otp_mail_threaded_forgot
from django.utils import timezone
from .models import SiteUser
from django.contrib.auth.hashers import make_password

@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp_for_register_email(request):
    try:
        email = request.data.get("email")

        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        if SiteUser.objects.filter(user__email = email).exists():
            return Response({"message": "This email already registered"})

        mail_status = send_otp_mail_threaded(email)

        if mail_status == 0:
            return Response({"message": "Something went wrong sending the email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
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

        return JsonResponse({"message": "OTP verified Success", "success": "true"})
    
    except Exception as e:
        return JsonResponse({"error": str(e)})
    
@api_view(["POST"])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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
        
        mail_status = send_otp_mail_threaded_forgot(email, first_name)

        return JsonResponse({"success":"True","message": "OTP sent Successfull"})
        
    except Exception as e:
        return JsonResponse({"error": str(e)})

@api_view(['POST'])
@permission_classes([AllowAny])
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

        return JsonResponse({"message": "verification success", "success": "true"})

    except Exception as e:
        return JsonResponse({"message":str(e)})

@api_view(['POST'])
def user_logout(request):
    try:
        if request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()
            return JsonResponse({"message": "Logout successful"})
        else:
            return JsonResponse({"error": "User not authenticated"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        user = request.user
        site_user = SiteUser.objects.get(user=user)
        user_site_user = User.objects.get(siteuser = site_user)
        addresses = UserAddress.objects.filter(user=site_user)


        address_list = []
        for addr in addresses:
            address_list.append({
                "address": addr.address,
                "city": addr.city,
                "state": addr.state,
                "country": addr.country,
                "pincode": addr.pincode,
            })

        user_data = {
            "name": user_site_user.first_name,
            "last_name": user_site_user.last_name,
            "email": user.email,
            "phone_number": site_user.phone_number,
            "profile_picture": request.build_absolute_uri(site_user.profile_picture.url) if site_user.profile_picture else None,
            "resume_link": request.build_absolute_uri(site_user.resume_link.url) if site_user.resume_link else None,
            "addresses": address_list,
        }

        return Response({"status": "success", "data": user_data}, status=status.HTTP_200_OK)

    except SiteUser.DoesNotExist:
        return Response({"status": "error", "message": "SiteUser profile not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_profile(request):
    try:
        user = request.user
        site_user = SiteUser.objects.get(user = user)

        site_user.delete()
        user.delete()
        return JsonResponse({"message": "User profile deleted successfully"}, status=204)
    
    except SiteUser.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_password(request):
    try:
        email = request.data.get('email')
        new_password = request.data.get('password')

        if not email or not new_password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            if user.check_password(new_password):
                return Response({'error': 'New password cannot be the same as the old password'}, status=status.HTTP_400_BAD_REQUEST)

            user.password = make_password(new_password)
            user.save()

            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)