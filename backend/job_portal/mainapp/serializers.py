from rest_framework import serializers
from .models import (
    SiteUser, Education, Experience, Skill, Certification, Language, Project, UserAddress, Employer
)

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = "__all__"

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = "__all__"

class SiteUserSerializer(serializers.ModelSerializer):
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    user_address = UserAddressSerializer(many=True, read_only=True)

    profile_completion = serializers.SerializerMethodField()

    class Meta:
        model = SiteUser
        fields = [
            "id", "user", "role", "profile_picture", "phone_number", "resume_link",
            "date_of_birth", "gender", "linkdin_url", "github_url", "portfolio_url",
            "education", "experience", "skills", "certifications", "languages",
            "projects", "user_address", "created_at", "updated_at", "profile_completion"
        ]

    def get_profile_completion(self, obj):
        return obj.profile_completion()
