from rest_framework import serializers
from .models import Job, Employer, Location

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['name', 'employer_logo', 'website']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['city', 'state', 'country']

class JobSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer()
    location = LocationSerializer()

    class Meta:
        model = Job
        fields = [
            'job_id', 'title', 'description', 'is_remote', 'employment_type',
            'posted_at', 'google_link', 'min_salary', 'max_salary', 'salary_period',
            'employer', 'location'
        ]
