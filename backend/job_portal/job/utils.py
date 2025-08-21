import os
import requests
from urllib.parse import urlparse
from django.conf import settings
from django.core.files.base import ContentFile
from .signals import job_created
from .models import Job, Employer, Location, ApplyOption, EmploymentType

BASE_URL = "https://jsearch.p.rapidapi.com/search"

def fetch_jobs(query="Python Developer", location="India", page=1):
    headers = {
        "x-rapidapi-key": settings.JSEARCH_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": f"{query} in {location}",
        "page": page
    }

    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")


def download_image_from_url(url):
    if not url:
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()

        file_name = os.path.basename(urlparse(url).path)
        if not file_name:
            file_name = "employer_logo.jpg"

        return ContentFile(response.content, name=file_name)

    except requests.exceptions.RequestException:
        return None


from django.db import transaction
def fetch_and_store_jobs(response):
    apply_options_to_create = []
    emp_types_to_create = []
    created_count = 0  

    for job_data in response.get('data', []):
        job_id = job_data['job_id']

        employer, _ = Employer.objects.update_or_create(
            name=job_data['employer_name'],
            defaults={'website': job_data.get('employer_website')}
        )
        logo_url = job_data.get('employer_logo')
        if logo_url:
            logo_file = download_image_from_url(logo_url)
            if logo_file:
                employer.employer_logo.save(logo_file.name, logo_file, save=True)

        location = None
        if job_data.get('job_city') and job_data.get('job_country'):
            location, _ = Location.objects.update_or_create(
                city=job_data['job_city'],
                state=job_data.get('job_state'),
                country=job_data['job_country'],
                defaults={
                    'latitude': job_data.get('job_latitude'),
                    'longitude': job_data.get('job_longitude'),
                }
            )

        apply_link = ''
        for apply_data in job_data.get('apply_options', []):
            if apply_data.get('is_direct'):
                apply_link = apply_data.get('apply_link')
                break
        if not apply_link and job_data.get('apply_options'):
            apply_link = job_data['apply_options'][0].get('apply_link')

        job, created = Job.objects.update_or_create(
            job_id=job_id,
            defaults={
                'title': job_data['job_title'],
                'description': job_data['job_description'],
                'is_remote': job_data['job_is_remote'],
                'employment_type': job_data.get('job_employment_type') or '',
                'posted_at': job_data['job_posted_at_datetime_utc'],
                'posted_timestamp': job_data['job_posted_at_timestamp'],
                'google_link': apply_link or '',
                'min_salary': job_data.get('job_min_salary'),
                'max_salary': job_data.get('job_max_salary'),
                'salary_period': job_data.get('job_salary_period') or '',
                'employer': employer,
                'location': location
            }
        )

        if created:
            created_count += 1  
            job_created.send(sender=Job, job_instance=job)

            for apply_data in job_data.get('apply_options', []):
                apply_options_to_create.append(ApplyOption(
                    job=job,
                    publisher=apply_data['publisher'],
                    apply_link=apply_data['apply_link'],
                    is_direct=apply_data['is_direct']
                ))

            for emp_type in job_data.get('job_employment_types', []):
                emp_types_to_create.append(EmploymentType(job=job, type=emp_type))

    if apply_options_to_create:
        ApplyOption.objects.bulk_create(apply_options_to_create, ignore_conflicts=True)
    if emp_types_to_create:
        EmploymentType.objects.bulk_create(emp_types_to_create, ignore_conflicts=True)

    return created_count