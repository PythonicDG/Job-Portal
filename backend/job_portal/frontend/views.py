from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import PageSection, SectionContent
from rest_framework.decorators import api_view
from headerfooter.models import SubMenu
from .models import *
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes



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






