from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DashboardHeader, SidebarItem
from .serializers import DashboardHeaderSerializer, SidebarItemSerializer


class DashboardConfigAPIView(APIView):
    def get(self, request, *args, **kwargs):
        header = DashboardHeader.objects.first()
        sidebar = SidebarItem.objects.all().order_by("order")

        header_data = DashboardHeaderSerializer(header).data if header else {}
        sidebar_data = SidebarItemSerializer(sidebar, many=True).data

        return Response({
            "header": header_data,
            "sidebar": sidebar_data
        })
