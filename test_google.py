import requests

url = "https://places.googleapis.com/v1/places:searchText"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": "fake_key",
    "X-Goog-FieldMask": "places.displayName.text,places.formattedAddress,places.websiteUri,places.rating,places.userRatingCount"
}

payload = {
    "textQuery": "plumbers in new york"
}

try:
    print("Calling Google Places API...")
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print("Status Code:", response.status_code)
    print("Response text:", response.text)
except Exception as e:
    print("Exception occurred:", type(e).__name__, str(e))
