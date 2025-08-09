from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Menu
from .serializers import MenuSerializer

class HeaderFooterView(APIView):
    def get(self, request):
        menus = Menu.objects.all().order_by('order')
        serializer = MenuSerializer(menus, many=True)
        return Response({'menus': serializer.data})
