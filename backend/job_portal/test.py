import requests

# -------------------------------
# CONFIG
# -------------------------------
GOOGLE_API_KEY = "AIzaSyCKlHnTGnsxIMH2nywK8kPwi1QUKcuDsWc"  # replace with your key
COMPANY_NAME = "Infosys"

# -------------------------------
# STEP 1: Find Place (get place_id)
# -------------------------------
find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
find_place_params = {
    "input": COMPANY_NAME,
    "inputtype": "textquery",
    "fields": "place_id",
    "key": GOOGLE_API_KEY
}

find_place_res = requests.get(find_place_url, params=find_place_params).json()
if not find_place_res.get("candidates"):
    print("Company not found")
    exit()

place_id = find_place_res["candidates"][0]["place_id"]
print(f"Place ID: {place_id}")

# -------------------------------
# STEP 2: Place Details
# -------------------------------
details_url = "https://maps.googleapis.com/maps/api/place/details/json"
details_params = {
    "place_id": place_id,
    "fields": ",".join([
        "name",
        "formatted_address",
        "geometry",
        "photos",
        "types",
        "formatted_phone_number",
        "international_phone_number",
        "website",
        "opening_hours",
        "price_level",
        "rating",
        "user_ratings_total"
    ]),
    "key": GOOGLE_API_KEY
}

details_res = requests.get(details_url, params=details_params).json()

if details_res.get("status") != "OK":
    print("Error fetching details:", details_res)
    exit()

company = details_res["result"]

# -------------------------------
# STEP 3: Print Data
# -------------------------------
print("\n--- Company Details ---")
print("Name:", company.get("name"))
print("Address:", company.get("formatted_address"))
print("Website:", company.get("website"))
print("Phone:", company.get("formatted_phone_number"))
print("Intl Phone:", company.get("international_phone_number"))
print("Rating:", company.get("rating"))
print("Total Reviews:", company.get("user_ratings_total"))
print("Price Level:", company.get("price_level"))
print("Types:", company.get("types"))
print("Open Now:", company.get("opening_hours", {}).get("open_now"))
print("Latitude:", company.get("geometry", {}).get("location", {}).get("lat"))
print("Longitude:", company.get("geometry", {}).get("location", {}).get("lng"))

# -------------------------------
# STEP 4: Process Photos
# -------------------------------
photos = company.get("photos", [])
photo_urls = []
for photo in photos:
    ref = photo.get("photo_reference")
    if ref:
        url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={ref}&key={GOOGLE_API_KEY}"
        photo_urls.append(url)

print("\nPhotos URLs:")
for url in photo_urls:
    print(url)

print("\n--- End of Company Data ---")
