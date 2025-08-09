import requests
from django.conf import settings


BASE_URL = "https://jsearch.p.rapidapi.com/search"

def fetch_jobs(query = "Python Developer", location = "India", page = 1):
    headers = {
        "x-rapidapi-key": settings.JSEARCH_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": f"{query} in {location}",
        "page": page
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

        