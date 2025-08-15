import requests
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .utils import fetch_jobs, fetch_and_store_jobs
from .models import Job, SidebarMenu, UserSavedJob, user_viewed_jobs, EmploymentType
from django.http import JsonResponse
from headerfooter.models import CompanyInfo
from rest_framework.pagination import PageNumberPagination
from math import ceil
from django.db.models import Q
from .serializer import JobSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.postgres.search import SearchVector

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
# @permission_classes([IsAuthenticated])
def jobs_list(request):
    queryset = Job.objects.all().select_related('employer', 'location') \
        .prefetch_related('apply_options', 'employment_types')
    
    search = request.GET.get('search', '').strip()
    location = request.GET.get('location', '')
    employment_type = request.GET.get('employment_type', '')
    min_salary = request.GET.get('min_salary')
    is_remote = request.GET.get('is_remote')
    
    # if search:
    #     queryset = queryset.filter(
    #         Q(title__icontains=search) |
    #         Q(description__icontains=search) |
    #         Q(employer__name__icontains=search) |
    #         Q(skills_required__icontains=search)
    #     ).distinct()

    if search:
        queryset = queryset.annotate(
            search_vector=SearchVector('title', 'description', 'employer__name', 'skills_required')
        ).filter(search_vector__icontains=search)
    
    if location:
        queryset = queryset.filter(
            Q(location__city__icontains=location) |
            Q(location__state__icontains=location) |
            Q(location__country__icontains=location)
        )
    
    if employment_type:
        queryset = queryset.filter(
            Q(employment_type__icontains=employment_type) |
            Q(employment_types__type__icontains=employment_type)
        ).distinct()
    
    if min_salary:
        try:
            min_salary_value = int(min_salary)
            queryset = queryset.filter(min_salary__gte=min_salary_value)
        except ValueError:
            pass
    
    if is_remote is not None:
            is_remote_bool = str(is_remote).lower() == 'true'
            queryset = queryset.filter(is_remote=is_remote_bool)
    
    queryset = queryset.order_by('-posted_at')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10  
    paginated_jobs = paginator.paginate_queryset(queryset, request)
    
    employment_types = sorted(list(set(
            filter(
                None,
                list(Job.objects.values_list('employment_type', flat=True).exclude(employment_type__isnull=True)) +
                list(EmploymentType.objects.values_list('type', flat=True))
            )
        )))

    
    data = []
    for job in paginated_jobs:
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
            } if job.location else None,
            "apply_options": [
                {
                    "id": option.id,
                    "publisher": option.publisher,
                    "apply_link": option.apply_link,
                    "is_direct": option.is_direct,
                } for option in job.apply_options.all()
            ],
        })


    return Response({
        "count": queryset.count(),
        "total_pages": ceil(queryset.count() / paginator.page_size) if paginator.page_size else 1,
        "current_page": request.GET.get('page', 1),
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "filters": {
            "employment_types": sorted(list(set(filter(None, employment_types)))),
        },
        "results": data
    })


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

@api_view(['DELETE'])
def unsave_job(request, job_id):
    try:
        job = Job.objects.get(job_id=job_id)

        saved_job = SavedJob.objects.get(user=request.user, job=job)
        saved_job.delete()

        return Response({"message": "Job unsaved successfully"}, status=204)

    except Job.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)
    except SavedJob.DoesNotExist:
        return Response({"error": "Saved job not found for user"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def view_job(request):
    try:
        if not request.user.is_authenticated:
            return Response({"error": "User not authenticated"}, status = 401)

        job_id = request.data.get('job_id')
        job = Job.objects.get(job_id = job_id)

        saved_job_instance, created = user_viewed_jobs.objects.get_or_create(
            user = request.user,
            job = job
        )

        if not created:
            return Response({"message": "Job already viewed"}, status=200)

        return Response({"message": "Job viewed successfully"}, status=201)

    except Job.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def recent_viewed_jobs(request):
    try:
        if not request.user.is_authenticated:
            return Response({"error": "User not authenticated"}, status=401)

        recent_viewed = user_viewed_jobs.objects.filter(user=request.user).order_by('-viewed_at')[:5]
        
        job_list = []
        for entry in recent_viewed:
            job = entry.job
            job_list.append({
                "job_id": job.job_id,
                "title": job.title,
                "company": job.employer.name, 
                "viewed_at": entry.viewed_at
            })

        return Response({"recent_jobs": job_list}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def dashboard_data(request):
    user = request.user

    viewed_count = user_viewed_jobs.objects.filter(user=user).count()

    saved_count = UserSavedJob.objects.filter(user=user).count()

    recent_viewed = (
        user_viewed_jobs.objects
        .filter(user=user)
        .select_related('job', 'job__employer', 'job__location')
        .order_by('-viewed_at')[:5]
    )
    recent_jobs_data = JobSerializer([view.job for view in recent_viewed], many=True).data

    recommended_jobs = Job.objects.all().order_by('-created_at')[:5]
    recommended_jobs_data = JobSerializer(recommended_jobs, many=True).data

    return Response({
        "viewed_jobs_count": viewed_count,
        "saved_jobs_count": saved_count,
        "recent_viewed_jobs": recent_jobs_data,
        "recommended_jobs": recommended_jobs_data
    })