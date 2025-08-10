from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SiteUser, ParsedResumeData
from .utils.resume_parser import parse_resume  
from mainapp.utils.resume_parser import parse_resume
import os

@receiver(post_save, sender=SiteUser)
def parse_resume_on_upload(sender, instance, created, **kwargs):
    if instance.resume_link:
        resume_path = instance.resume_link.path
        full_text = parse_resume(resume_path)

        keywords = [
            "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust", "Ruby", "Kotlin", "Swift", "PHP", "Scala", "Perl",

            "HTML", "CSS", "SASS", "LESS", "React", "Angular", "Vue", "Next.js", "Nuxt.js", "Tailwind", "Bootstrap", "jQuery",

            "Django", "Flask", "FastAPI", "Express", "Spring", "Laravel", ".NET", "Ruby on Rails", "NestJS",

            "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "Cassandra", "Elasticsearch", "Firebase",

            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Jenkins", "GitLab CI", "Terraform", "Ansible", "Nginx", "Apache",

            "Git", "GitHub", "Bitbucket", "Jira", "Postman", "Figma", "Slack", "Trello", "Notion",

            "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "Keras", "PyTorch", "OpenCV", "NLP", "Computer Vision", "Data Analysis", "Data Science",

            "Selenium", "Cypress", "JUnit", "PyTest", "Mocha", "Chai", "Postman", "TestNG",

            "Teamwork", "Leadership", "Communication", "Problem Solving", "Agile", "Scrum",

            "REST", "GraphQL", "WebSockets", "Microservices", "Linux", "Unix", "Shell Scripting", "API Integration"
        ]

        skills = [word for word in keywords if word.lower() in full_text.lower()]

        ParsedResumeData.objects.update_or_create(
            user=instance,
            defaults={
                'full_text': full_text,
                'skills': ", ".join(skills),
            }
        )
