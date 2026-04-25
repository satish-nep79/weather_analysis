
from datetime import datetime
import json

import requests

class WeatherAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.weatherbit.io/v2.0"
        self.city_name = "Pokhara"
        
    
    def get_current_forecast(self):
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
        
    # Parse raw API Data
    # Extract relevant fields and convert to a list of dictionaries for database insertion
    def parse_forecast(self, raw_data):
        if not raw_data or "data" not in raw_data:
            print("No data found in API response.")
            return []

        records = []
        for entry in raw_data["data"]:
            try:
                date = datetime.strptime(entry["datetime"], "%Y-%m-%d")
                records.append({
                    "forecast_date":          entry["datetime"],
                    "year":                   date.year,
                    "month":                  date.month,
                    "month_name":             date.strftime("%B"),
                    "avg_temp_c":             float(entry["temp"]),
                    "max_temp_c":             float(entry["max_temp"]),
                    "min_temp_c":             float(entry["min_temp"]),
                    "precip_mm":              float(entry["precip"]) if entry["precip"] else 0.0,
                    "precip_probability_pct": int(entry["pop"]),
                    "humidity_pct":           int(entry["rh"]),
                    "wind_speed_ms":          float(entry["wind_spd"]),
                    "wind_gust_ms":           float(entry["wind_gust_spd"]),
                    "wind_direction":         entry["wind_cdir"],
                    "cloud_cover_pct":        int(entry["clouds"]),
                    "visibility_km":          float(entry["vis"]) if entry["vis"] else None,
                    "uv_index":               float(entry["uv"]),
                    "dewpoint_c":             float(entry["dewpt"]),
                    "pressure_hpa":           int(entry["pres"]),
                    "weather_description":    entry["weather"]["description"],
                    "data_source":            "Weatherbit API"
                })
            except Exception as e:
                print(f"Skipping entry {entry.get('datetime', 'unknown')}: {e}")
                continue

        print(f"Parsed {len(records)} forecast records.")
        return records