from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Menu, CompanyInfo
from .serializers import MenuSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Footer
from rest_framework.permissions import AllowAny

class HeaderFooterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        menus = Menu.objects.all().order_by('order')
        menu_serializer = MenuSerializer(menus, many=True)

        company_info = CompanyInfo.objects.first()
        logo_url = company_info.logo.url if company_info and company_info.logo else None

        return Response({
            'menus': menu_serializer.data,
            'company_logo': request.build_absolute_uri(logo_url) if logo_url else None
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def footer_detail(request):
    try:
        footer = Footer.objects.prefetch_related(
            'footer_menus__items', 'social_links', 'legal_links'
        ).first()

        if not footer:
            return Response({'error': 'Footer not found'}, status=404)

        # Try to get contact_info safely
        try:
            contact_info = footer.contact_info
            contact_info_data = {
                'email': contact_info.email,
                'phone': contact_info.phone,
                'address': contact_info.address
            }
        except:
            contact_info_data = None

        data = {
            'company_name': footer.company_name,
            'logo': footer.logo.url if footer.logo else None,
            'legal_text': footer.legal_text,
            'background_color': footer.background_color,
            'text_color': footer.text_color,
            'border_color': footer.border_color,
            'contact_info': contact_info_data,
            'menus': [
                {
                    'title': menu.title,
                    'items': [
                        {'name': item.name, 'link': item.link}
                        for item in menu.items.all()
                    ]
                }
                for menu in footer.footer_menus.all()
            ],
            'social_links': [
                {
                    'name': social.name,
                    'icon': social.icon,
                    'link': social.link
                }
                for social in footer.social_links.all()
            ],
            'legal_links': [
                {
                    'name': legal.name,
                    'link': legal.link
                }
                for legal in footer.legal_links.all()
            ]
        }

        return Response(data)
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)