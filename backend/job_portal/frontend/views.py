from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import PageSection, SectionContent
from rest_framework.decorators import api_view
from headerfooter.models import SubMenu
from .models import *
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from .utils import send_contact_email
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def fetch_records(request):

    slug = request.GET.get('slug')
    submenu = SubMenu.objects.get(slug=slug)

    if not submenu:
        return JsonResponse({
            "result": False,
            "error": "page not found"
        })
        
    page_sections = PageSection.objects.filter(submenu = submenu, is_active = True)

    data = {
        "result": True,
        "title": submenu.title,
        "slug": slug,
        "sections": []
    }

    sections_data = []
    result = []

    for section in page_sections:
        section_content = SectionContent.objects.filter(section=section, is_active = True).order_by('sequence')
        content_data = []

        for content in section_content:
            content_data.append({
                "title": content.title,
                "description": content.description,
                "icon_url": content.icon.url if content.icon else None,
                "icon_alternate_text": content.icon_alternate_text,
                "button_text": content.button_text,
                "button_url": content.button_url,
            })

        data['sections'].append({
            "section_type": section.section_type,
            "heading": section.heading,
            "description": section.description,
            "logo": section.logo.url if section.logo else None,
            "logo_alternate_text": section.logo_alt_text,
            "slogan": section.slogan,
            "button_text": section.button_text,
            "button_url": section.button_url,
            "image_url": section.image.url if section.image else None,
            "image_alternate_text": section.image_alt_text,
            "background_image": section.background_image.url if section.background_image else None,
            "background_image_alternate_text": section.background_image_alt_text,
            "contents": content_data
        })
    
    return JsonResponse(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_us(request):
    try:
        email = request.data.get("email")
        name = request.data.get("name")
        message = request.data.get("message")
        
        if not email:
            return Response({"error": "email required"})
        
        if not name:
            return Response({"error": "name required"})
        
        contact_us_instance = ContactUs.objects.create(
            email=email,
            name=name,
            message=message
        )

        send_contact_email(name, email, message)

        return JsonResponse({"message": "success"})

    except Exception as e:
        return JsonResponse({"Error": str(e)})

@api_view(['GET'])
@permission_classes([AllowAny])
def faq_list(request):
    sections_data = []

    for section in FAQSection.objects.all():
        categories_data = []

        for category in section.categories.all():
            questions_data = []

            for q in category.questions.all():
                questions_data.append({
                    "question": q.question,
                    "answer": q.answer,
                })

            categories_data.append({
                "title": category.title,
                "questions": questions_data,
            })

        sections_data.append({
            "title": section.title,
            "categories": categories_data,
        })

    return JsonResponse({"sections": sections_data})