import requests
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .utils import fetch_jobs, fetch_and_store_jobs
from .models import Job, SidebarMenu, UserSavedJob, user_viewed_jobs, EmploymentType, ProfileButtonItem, Notification
from django.http import JsonResponse
from headerfooter.models import CompanyInfo
from rest_framework.pagination import PageNumberPagination
from math import ceil
from django.db.models import Q
from .serializer import JobSerializer, ProfileButtonSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.postgres.search import SearchVector
import re
from mainapp.models import SiteUser
from .signals import jobs_synced

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
        
        total_new_jobs = 0
        
        for query in queries:
            response = fetch_jobs(query=query, location=location, page=page)
            new_jobs_count = fetch_and_store_jobs(response)
            total_new_jobs += new_jobs_count
        
        jobs_synced.send(sender=None, total_jobs=total_new_jobs)
        
        return Response({
            "status": "success",
            "message": f"Jobs synced successfully for {len(queries)} job roles."
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def str_to_bool(val):
    if val is None:
        return None
    v = str(val).strip().lower()
    if v in ("1", "true", "yes", "on"):  return True
    if v in ("0", "false", "no", "off"): return False
    return None

@api_view(['GET'])
@permission_classes([AllowAny])
def jobs_list(request):
    qs = Job.objects.select_related('employer', 'location') \
        .prefetch_related('apply_options')  

    search = (request.GET.get('search') or '').strip()
    location = (request.GET.get('location') or '').strip()
    emp_type = (request.GET.get('employment_type') or '').strip()
    min_salary = request.GET.get('min_salary')
    is_remote = str_to_bool(request.GET.get('is_remote'))

    if search:
        terms = [t for t in re.split(r'\s+', search) if t]
        for term in terms:
            qs = qs.filter(
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(location__state__icontains=term) |
                Q(location__country__icontains=term)
            )

    if location:
        qs = qs.filter(
            Q(location__city__icontains=location) |
            Q(location__state__icontains=location) |
            Q(location__country__icontains=location)
        )

    if emp_type:
        qs = qs.filter(
            Q(employment_type__icontains=emp_type) |
            Q(employment_types__type__icontains=emp_type) 
        )

    if min_salary not in (None, ''):
        try:
            qs = qs.filter(min_salary__gte=float(min_salary))
        except (TypeError, ValueError):
            pass

    if is_remote is not None:
        qs = qs.filter(is_remote=is_remote)

    qs = qs.distinct().order_by('-posted_at', '-id')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    page_objs = paginator.paginate_queryset(qs, request)

    job_types = list(
        Job.objects.exclude(employment_type__isnull=True)
                   .exclude(employment_type__exact='')
                   .values_list('employment_type', flat=True)
    )
    try:
        extra_types = list(EmploymentType.objects.values_list('type', flat=True))
    except Exception:
        extra_types = []
    employment_types = sorted(set(filter(None, job_types + extra_types)))

    results = []
    for job in page_objs:
        results.append({
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
                "employer_logo": job.employer.employer_logo.url if getattr(job.employer, "employer_logo", None) else None,
                "website": job.employer.website,
            },
            "location": ({
                "id": job.location.id,
                "city": job.location.city,
                "state": job.location.state,
                "country": job.location.country,
            } if job.location else None),
            "apply_options": [
                {
                    "id": opt.id,
                    "publisher": opt.publisher,
                    "apply_link": opt.apply_link,
                    "is_direct": opt.is_direct,
                } for opt in job.apply_options.all()
            ],
        })

    total = qs.count()
    return Response({
        "count": total,
        "total_pages": ceil(total / paginator.page_size) if paginator.page_size else 1,
        "current_page": int(request.GET.get('page', 1) or 1),
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "filters": {"employment_types": employment_types},
        "results": results,
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

        saved_job = UserSavedJob.objects.get(user=request.user, job=job)
        saved_job.delete()

        return Response({"message": "Job unsaved successfully"}, status=204)

    except Job.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)
    except UserSavedJob.DoesNotExist:
        return Response({"error": "Saved job not found for user"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_saved_jobs(request):
    user = request.user
    saved_jobs = UserSavedJob.objects.filter(user=user).select_related('job__employer', 'job__location').prefetch_related('job__apply_options')

    jobs_data = [JobSerializer(sj.job).data for sj in saved_jobs]

    return Response({
        "status": "success",
        "user": user.username,
        "saved_jobs": jobs_data
    })

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

@api_view(['GET'])
def profile_button_items(request):
    items = ProfileButtonItem.objects.filter(visible=True).order_by('order')
    serializer = ProfileButtonSerializer(items, many=True)
    return Response({
        "status": "success",
        "items": serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    user = request.user
    site_user = SiteUser.objects.get(user=user)
    
    unread_notifications = site_user.notifications.filter(is_read=False).order_by('-created_at')
    
    data = [{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at
    } for n in unread_notifications]

    return Response({"notifications": data})


@api_view(['POST'])
def mark_notification_read(request):
    user = request.user
    site_user = SiteUser.objects.get(user=user)
    notification_id = request.data.get('notification_id')

    if not notification_id:
        return Response({"status": "error", "message": "Notification ID is required."}, status=400)
    try:
        notification = site_user.notifications.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return Response({"status": "success", "message": "Notification marked as read."})
    except Notification.DoesNotExist:
        return Response({"status": "error", "message": "Notification not found."}, status=404)

@api_view(['POST'])
def mark_all_notifications_read(request):
    user = request.user
    site_user = SiteUser.objects.get(user=user)
    
    site_user.notifications.update(is_read=True)
    return Response({"status": "success", "message": "All notifications marked as read."})
