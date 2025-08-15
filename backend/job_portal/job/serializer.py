from rest_framework import serializers
from .models import Job, Employer, Location, ApplyOption, ProfileButtonItem

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['name', 'employer_logo', 'website']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['city', 'state', 'country']

class ApplyOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplyOption
        fields = ['apply_link', 'publisher']

class JobSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer()
    location = LocationSerializer()
    apply_option = serializers.SerializerMethodField() 

    class Meta:
        model = Job
        fields = [
            'job_id', 'title', 'is_remote', 'employment_type',
            'posted_at', 'google_link', 'min_salary', 'max_salary', 'salary_period',
            'employer', 'location', 'apply_option'
        ]
    def get_apply_option(self, obj):
        first_option = obj.apply_options.first()  # related_name from model
        if first_option:
            return ApplyOptionSerializer(first_option).data
        return None
    

class ProfileButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileButtonItem
        fields = ['id', 'label', 'icon', 'path', 'action', 'type', 'visible', 'order']