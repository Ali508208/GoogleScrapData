import requests
import time
import random

def get_google_places_api_data(api_key, query, next_page_token=None):
    """Fetch data from Google Places API for a specific search query with pagination."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    # Set up parameters
    params = {
        "query": query,  # For example, "restaurants in New York, USA"
        "key": api_key
    }
    
    if next_page_token:
        params["pagetoken"] = next_page_token
    
    # Retry logic for failed requests
    for attempt in range(5):  # Retry up to 5 times
        try:
            # Make the API request with a timeout
            response = requests.get(url, params=params, timeout=10)  # 10 seconds timeout
            if response.status_code != 200:
                raise Exception(f"Error fetching data from Google Places API: {response.text}")
            data = response.json()
            return data
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"Attempt {attempt + 1} failed with error: {str(e)}")
            # Wait a random time before retrying to avoid hitting the server too fast
            time.sleep(random.uniform(3, 6))  # Random sleep between 3 and 6 seconds
    raise Exception("Failed to fetch data from Google Places API after 5 attempts.")

def get_place_details(api_key, place_id):
    """Fetch detailed information for a specific place from Google Places API."""
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "place_id": place_id,
        "key": api_key
    }
    
    # Retry logic for failed requests
    for attempt in range(5):  # Retry up to 5 times
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Error fetching place details: {response.text}")
            data = response.json()
            return data["result"]
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"Attempt {attempt + 1} failed with error: {str(e)}")
            time.sleep(random.uniform(3, 6))  # Random sleep to avoid retrying too fast
    raise Exception("Failed to fetch place details after 5 attempts.")

def get_image_url(api_key, photo_reference):
    """Generate the image URL from Google Place Photo API using the photo_reference."""
    if not photo_reference:
        return None
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"

def scrape_google_maps_with_api(api_key, industry, city, country):
    """Fetch business data using Google Places API for a given industry, city, and country."""
    query = f"{industry} in {city}, {country}"
    
    all_results = []
    next_page_token = None

    while True:
        data = get_google_places_api_data(api_key, query, next_page_token)
        
        places = data.get("results", [])
        
        for place in places:
            place_id = place["place_id"]
            details = get_place_details(api_key, place_id)
            
            place_data = {
                "Name": details.get("name", "N/A"),
                "Rating": details.get("rating", "N/A"),
                "Address": details.get("formatted_address", "N/A"),
                "Image": None,  
                "Visited Link": details.get("url", "N/A"),
            }

            if "photos" in details:
                photo_reference = details["photos"][0].get("photo_reference")
                if photo_reference:
                    place_data["Image"] = get_image_url(api_key, photo_reference)

            all_results.append(place_data)
        
        next_page_token = data.get("next_page_token", None)
        if not next_page_token:
            break

        time.sleep(2)  # Random delay to avoid hitting rate limits

    return all_results
