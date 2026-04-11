
import json

import requests

class WetherAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.weatherbit.io/v2.0"
        self.city_name = "Pokhara"
        
    
    def get_current_forcase(self):
        params = {
            "city": self.city_name,
            "key": self.api_key 
        }
        
        try:
            url= f"{self.base_url}/forecast/daily"
            
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print(f"API Request URL: {json.dumps(response.url, indent=4)}")  # Print the full request URL for debugging
            
            return response.json()  # Return the JSON response as a dictionary
        except Exception as e:
            print(f"Error fetching current weather data: {e}")
            return None