from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Menu, CompanyInfo
from .serializers import MenuSerializer
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
