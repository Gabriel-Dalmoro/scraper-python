import os
import re
import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables from .env file if it exists
load_dotenv()

app = FastAPI(title="Google Places Scraper & Crawler")

class ScrapeRequest(BaseModel):
    search_query: str

class CrawlRequest(BaseModel):
    url: str

@app.post("/scrape")
def scrape_places(request: ScrapeRequest):
    api_key = os.environ.get("Maps_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Maps_API_KEY not found in environment")

    # Make request to Google Places API (New)
    url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName.text,places.formattedAddress,places.websiteUri,places.rating,places.userRatingCount,nextPageToken"
    }
    
    filtered_places = []
    page_token = ""
    
    for _ in range(3):
        payload = {
            "textQuery": request.search_query
        }
        if page_token:
            payload["pageToken"] = page_token
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
        except requests.exceptions.HTTPError as e:
            # If the API fails with a known HTTP error, extract Google's explanation JSON if possible
            raise HTTPException(status_code=500, detail=f"Google Places API Error: {response.text}")
        except requests.exceptions.RequestException as e:
            # If the Google API fails on the network level
            raise HTTPException(status_code=500, detail=f"Failed to communicate with Google Places API: {str(e)}")

        places = data.get("places", [])
        
        # Filter out places that do not have a websiteUri
        for place in places:
            if place.get("websiteUri"):
                filtered_places.append({
                    "displayName": place.get("displayName", {}).get("text", ""),
                    "formattedAddress": place.get("formattedAddress", ""),
                    "websiteUri": place.get("websiteUri", ""),
                    "rating": place.get("rating"),
                    "userRatingCount": place.get("userRatingCount")
                })
                
        page_token = data.get("nextPageToken")
        if not page_token:
            break
            
        time.sleep(2)

    return filtered_places

@app.post("/crawl")
def crawl_website(request: CrawlRequest):
    url = request.url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
        
        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Strip script, style, and hidden elements
        for element in soup(["script", "style", "noscript", "meta", "head", "title"]):
            element.extract()
            
        for hidden in soup.find_all(attrs={"style": re.compile(r"display:\s*none|visibility:\s*hidden", re.I)}):
            hidden.extract()
            
        for hidden_input in soup.find_all("input", type="hidden"):
            hidden_input.extract()
            
        # Extract text from body or whole document
        if soup.body:
            raw_text = soup.body.get_text(separator=' ', strip=True)
        else:
            raw_text = soup.get_text(separator=' ', strip=True)
            
        # Clean up excess whitespace
        website_text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Regex to scan for first valid email address
        # We also check the raw HTML content directly to find unrendered mailto links or hidden tags if needed.
        # But generally, scanning html_content directly is completely fine for extracting an email address.
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html_content)
        found_email = email_match.group(0) if email_match else None
        
        return {
            "url": url,
            "email": found_email,
            "website_text": website_text
        }
        
    except Exception as e:
        # DO NOT throw 500 error, instead return graceful empty 200 payload
        return {
            "url": url,
            "email": None,
            "website_text": ""
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
