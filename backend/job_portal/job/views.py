import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def job_listings(request):

    api_url = "https://jsearch.p.rapidapi.com/search"

    search = request.GET.get('search', '')
    params = {
        "query": search,
        "page": 1,
        "num_pages": 1
    }

    headers = {
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY"  
    }

    try:
      
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', [])
            return Response(jobs, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": f"Failed to fetch jobs from JSearch API. Status code: {response.status_code}"},
                status=status.HTTP_502_BAD_GATEWAY
            )
    except requests.exceptions.RequestException as e:
        return Response(
            {"error": f"Error during API request: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)