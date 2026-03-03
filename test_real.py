import requests
import json

response = requests.post(
    "http://127.0.0.1:8011/scrape",
    json={"search_query": "plumbers in new york"}
)
print("Status Code:", response.status_code)
if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data)} results")
    if data:
        print("First result snippet:")
        print(json.dumps(data[0], indent=2))
else:
    print("Error:", response.text)
