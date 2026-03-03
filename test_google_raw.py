import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.environ.get("Maps_API_KEY")

url = "https://places.googleapis.com/v1/places:searchText"
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": api_key,
    "X-Goog-FieldMask": "places.displayName.text,places.formattedAddress,places.websiteUri,places.rating,places.userRatingCount"
}

payload = {
    "textQuery": "plumbers in new york"
}

response = requests.post(url, headers=headers, json=payload, timeout=15)
print("Status Code:", response.status_code)
print("Response Text:", response.text)
