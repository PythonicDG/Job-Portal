import requests
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .utils import fetch_jobs, fetch_and_store_jobs
from .models import Job, SidebarMenu, UserSavedJob
from django.http import JsonResponse
from headerfooter.models import CompanyInfo

@api_view(['POST'])
@permission_classes([AllowAny])
def sync_jobs(request):
    try:
        location = request.data.get("location", "India")
        page = request.data.get("page", 1)

        queries = [
            "Python Developer",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "DevOps Engineer",
            "Data Scientist",
            "Machine Learning Engineer",
            "React Developer",
            "Node.js Developer",
            "Software Engineer"
        ]

        for query in queries:
            response = fetch_jobs(query=query, location=location, page=page)
            fetch_and_store_jobs(response)

        return Response({
            "status": "success",
            "message": f"Jobs synced successfully for {len(queries)} job roles."
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def jobs_list(request):
    jobs = Job.objects.all().select_related('employer', 'location').prefetch_related('apply_options', 'employment_types').order_by('-posted_at')

    data = []
    for job in jobs:
        data.append({
            "job_id": job.job_id,
            "title": job.title,
            "description": job.description,
            "is_remote": job.is_remote,
            "employment_type": job.employment_type,
            "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            "posted_timestamp": job.posted_timestamp,
            "google_link": job.google_link,
            "min_salary": job.min_salary,
            "max_salary": job.max_salary,
            "salary_period": job.salary_period,
            "employer": {
                "id": job.employer.id,
                "name": job.employer.name,
                "employer_logo": job.employer.employer_logo.url if job.employer.employer_logo else None,
                "website": job.employer.website,
            },
            "location": {
                "id": job.location.id if job.location else None,
                "city": job.location.city if job.location else None,
                "state": job.location.state if job.location else None,
                "country": job.location.country if job.location else None,
                "latitude": job.location.latitude if job.location else None,
                "longitude": job.location.longitude if job.location else None,
            } if job.location else None,
            "apply_options": [
                {
                    "id": option.id,
                    "publisher": option.publisher,
                    "apply_link": option.apply_link,
                    "is_direct": option.is_direct,
                } for option in job.apply_options.all()
            ],
            "employment_types": [
                {
                    "id": et.id,
                    "type": et.type,
                } for et in job.employment_types.all()
            ],
        })

    return Response(data)

@api_view(['GET'])
def sidebar_menu_list(request):
    menus = SidebarMenu.objects.all().order_by('order')
    company_info = CompanyInfo.objects.first()

    logo_url = company_info.logo.url if company_info and company_info.logo else None

    menu_data = [
        {
            "title": menu.title,
            "url": menu.url,
            "icon": menu.icon.url if menu.icon else None
        }
        for menu in menus
    ]

    return JsonResponse({
        "logo": logo_url,
        "menus": menu_data
    })

@api_view(['POST'])
def save_jobs(request):
    try:
        if not request.user.is_authenticated:
            return Response({"error": "User not authenticated"}, status = 401)

        job_id = request.data.get('job_id')
        job = Job.objects.get(job_id = job_id)

        saved_job_instance, created = UserSavedJob.objects.get_or_create(
            user = request.user,
            job = job
        )

        if not created:
            return Response({"message": "Job already saved"}, status=200)

        return Response({"message": "Job saved successfully"}, status=201)

    except Job.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

