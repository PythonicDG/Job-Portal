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
from .models import (
    SiteUser, Education, Experience, Skill, Certification, Language, Project, UserAddress, Employer
)
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from .serializers import SiteUserSerializer
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
            role = request.data.get("role")
            email = request.data.get("email")
            password = request.data.get("password")
            otp = request.data.get("otp")

            if role not in ["employee", "employer"]:
                return JsonResponse({"error": "Invalid role"}, status=400)

            otp_instance = VerifyEmailOtp.objects.filter(email=email, otp=otp).first()
            if not otp_instance:
                return JsonResponse({"error": "Invalid OTP"}, status=400)
            if timezone.now() > otp_instance.expires_at:
                return JsonResponse({"error": "OTP Expired"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "User with this Email already exists"}, status=400)

            user = User.objects.create_user(username=email, email=email, password=password)

            if role == "employee":
                first_name = request.data.get("first_name")
                last_name = request.data.get("last_name")
                phone_number = request.data.get("phone_number")
                profile_picture = request.FILES.get("profile_picture")
                resume_link = request.FILES.get("resume_link")

                user.first_name = first_name
                user.last_name = last_name
                user.save()

                site_user = SiteUser.objects.create(
                    user=user,
                    role="employee",
                    phone_number=phone_number,
                    profile_picture=profile_picture,
                    resume_link=resume_link,
                )

                UserAddress.objects.create(
                    user=site_user,
                    address=request.data.get("address"),
                    city=request.data.get("city"),
                    state=request.data.get("state"),
                    country=request.data.get("country"),
                    pincode=request.data.get("pincode"),
                )

            elif role == "employer":
                company_data = request.data.get("company", {})
                compliance_data = request.data.get("compliance", {})

                employer = Employer.objects.create(
                    user=user,
                    company_name=company_data.get("name"),
                    company_phone=company_data.get("phone"),
                    company_website=company_data.get("website"),
                    industry_type=company_data.get("industry"),
                    company_size=company_data.get("size"),
                    company_logo=request.FILES.get("logo"),
                    description=company_data.get("description"),
                    pan_gst=compliance_data.get("panGst"),
                    brc_file=request.FILES.get("brcFile"),
                )

                address_data = company_data.get("address", {})
                EmployerAddress.objects.create(
                    employer=employer,
                    street=address_data.get("street"),
                    city=address_data.get("city"),
                    state=address_data.get("state"),
                    pincode=address_data.get("pincode"),
                    country=address_data.get("country"),
                )

            otp_instance.delete()

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
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            role = None
            profile = {}

            if hasattr(user, "siteuser") and user.siteuser is not None:
                role = user.siteuser.role  
                profile = {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.siteuser.phone_number,
                    "resume_link": user.siteuser.resume_link.url if user.siteuser.resume_link else None,
                    "profile_picture": user.siteuser.profile_picture.url if user.siteuser.profile_picture else None,
                }

            elif hasattr(user, "employer_profile") and user.employer_profile is not None:
                role = "employer"
                profile = {
                    "company_name": user.employer_profile.company_name,
                    "company_phone": user.employer_profile.company_phone,
                    "company_website": user.employer_profile.company_website,
                    "industry_type": user.employer_profile.industry_type,
                    "company_size": user.employer_profile.company_size,
                    "company_logo": user.employer_profile.company_logo.url if user.employer_profile.company_logo else None,
                }

            return Response({
                "message": "Login success",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": role,
                    "profile": profile
                }
            })

        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
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

            return Response({'message': 'Password updated successfully', 'success': 'true'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    try:
        user = request.user
        site_user = SiteUser.objects.get(user=user)

        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone_number = request.data.get('phone_number')
        profile_picture = request.FILES.get('profile_picture')
        resume = request.FILES.get('resume')

        address_id = request.data.get('address_id') 
        address = request.data.get('address')
        city = request.data.get('city')
        state = request.data.get('state')
        country = request.data.get('country')
        pincode = request.data.get('pincode')

        if first_name is not None:
            site_user.user.first_name = first_name
        if last_name is not None:
            site_user.user.last_name = last_name
        if phone_number is not None:
            site_user.phone_number = phone_number
        if profile_picture is not None:
            site_user.profile_picture = profile_picture
        if resume is not None:
            site_user.resume_link = resume

        site_user.save()
        site_user.user.save()

        user_address = UserAddress.objects.get(user=site_user)

        if user_address:
            if address is not None:
                user_address.address = address
            if city is not None:
                user_address.city = city
            if state is not None:
                user_address.state = state
            if country is not None:
                user_address.country = country
            if pincode is not None:
                user_address.pincode = pincode


            user_address.save()

        return JsonResponse({"message": "User profile and address updated successfully"}, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({"error": "SiteUser profile not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@api_view(['POST'])
def complete_profile(request):
    user = request.user
    site_user = SiteUser.objects.get(user=user)

    site_user.date_of_birth = request.data.get('date_of_birth', site_user.date_of_birth)
    site_user.gender = request.data.get('gender', site_user.gender)
    site_user.linkdin_url = request.data.get('linkedin_url', site_user.linkdin_url)
    site_user.github_url = request.data.get('github_url', site_user.github_url)
    site_user.portfolio_url = request.data.get('portfolio_url', site_user.portfolio_url)
    site_user.updated_at = timezone.now()
    site_user.save()


    education_list = request.data.get('education', [])
    for edu in education_list:
        Education.objects.update_or_create(
            user=site_user,
            degree=edu.get('degree'),
            institution=edu.get('institution'),
            defaults={
                'field_of_study': edu.get('field_of_study'),
                'start_year': edu.get('start_year'),
                'end_year': edu.get('end_year'),
                'grade': edu.get('grade')
            }
        )

    experience_list = request.data.get('experience', [])
    for exp in experience_list:
        Experience.objects.update_or_create(
            user=site_user,
            job_title=exp.get('job_title'),
            company_name=exp.get('company_name'),
            defaults={
                'start_date': exp.get('start_date'),
                'end_date': exp.get('end_date'),
                'is_current': exp.get('is_current', False),
                'description': exp.get('description')
            }
        )

    skills_list = request.data.get('skills', [])
    for skill in skills_list:
        Skill.objects.update_or_create(
            user=site_user,
            name=skill.get('name'),
            defaults={
                'proficiency': skill.get('proficiency', 'Beginner')
            }
        )

    projects_list = request.data.get('projects', [])
    for project in projects_list:
        Project.objects.update_or_create(
            user=site_user,
            title=project.get('title'),
            defaults={
                'description': project.get('description'),
                'technologies': project.get('technologies'),
                'start_date': project.get('start_date'),
                'end_date': project.get('end_date'),
                'is_ongoing': project.get('is_ongoing', False),
                'project_url': project.get('project_url'),
                'repo_url': project.get('repo_url')
            }
        )

    cert_list = request.data.get('certifications', [])
    for cert in cert_list:
        Certification.objects.update_or_create(
            user=site_user,
            name=cert.get('name'),
            defaults={
                'issuer': cert.get('issuer'),
                'date_obtained': cert.get('date_obtained')
            }
        )

    languages_list = request.data.get('languages', [])
    for lang in languages_list:
        Language.objects.update_or_create(
            user=site_user,
            name=lang.get('name'),
            defaults={'proficiency': lang.get('proficiency', 'Basic')}
        )

    response_data = {
        "message": "Profile updated successfully",
        "profile_completion": site_user.profile_completion()
    }

    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_complete_profile(request):
    user = request.user
    site_user = SiteUser.objects.get(user=user)

    serializer = SiteUserSerializer(site_user)
    return Response(serializer.data)