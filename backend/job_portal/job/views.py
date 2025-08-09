import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import fetch_jobs

@api_view(["GET"])
def job_listings(request):
    query = request.GET.get("query", "Python Developer")
    location = request.GET.get("location", "India")
    page = int(request.GET.get("page", 1))
    data = fetch_jobs(query, location, page)
    return Response(data)
