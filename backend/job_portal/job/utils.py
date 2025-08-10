import os
import requests
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.base import ContentFile

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


def fetch_and_store_jobs(response):
    for job_data in response.get('data', []):
        job_id = job_data['job_id']
        if Job.objects.filter(job_id=job_id).exists():
            continue

        logo_file = download_image_from_url(job_data.get('employer_logo'))

        employer, created = Employer.objects.get_or_create(
            name=job_data['employer_name'],
            website=job_data.get('employer_website'),
        )

        if logo_file and (created or not employer.employer_logo):
            employer.employer_logo.save(logo_file.name, logo_file)

        location = None
        if job_data.get('job_city') and job_data.get('job_country'):
            location, _ = Location.objects.get_or_create(
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

        job = Job.objects.create(
            job_id=job_id,
            title=job_data['job_title'],
            description=job_data['job_description'],
            is_remote=job_data['job_is_remote'],
            employment_type=job_data.get('job_employment_type') or '',
            posted_at=job_data['job_posted_at_datetime_utc'],
            posted_timestamp=job_data['job_posted_at_timestamp'],
            google_link=apply_link or '',
            min_salary=job_data.get('job_min_salary'),
            max_salary=job_data.get('job_max_salary'),
            salary_period=job_data.get('job_salary_period') or '',
            employer=employer,
            location=location
        )

        for apply_data in job_data.get('apply_options', []):
            ApplyOption.objects.create(
                job=job,
                publisher=apply_data['publisher'],
                apply_link=apply_data['apply_link'],
                is_direct=apply_data['is_direct']
            )

        for emp_type in job_data.get('job_employment_types', []):
            EmploymentType.objects.create(job=job, type=emp_type)
