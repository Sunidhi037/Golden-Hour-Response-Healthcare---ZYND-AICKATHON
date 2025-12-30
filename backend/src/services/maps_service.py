import httpx
from config import get_settings

settings = get_settings()

class MapsService:
    def __init__(self):
        self.base_url = settings.osrm_server

    async def get_route_details(self, start_coords: tuple, end_coords: tuple):
        """
        Get route data from OSRM.
        Args: start_coords (lat, lon), end_coords (lat, lon)
        """
        # OSRM expects: longitude,latitude
        start_str = f"{start_coords[1]},{start_coords[0]}"
        end_str = f"{end_coords[1]},{end_coords[0]}"
        
        url = f"{self.base_url}/route/v1/driving/{start_str};{end_str}"
        params = {"overview": "full", "geometries": "geojson"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == "Ok" and data.get("routes"):
                        route = data["routes"][0]
                        return {
                            "distance_km": round(route["distance"] / 1000, 2),
                            "duration_min": round(route["duration"] / 60, 0),
                            "geometry": route["geometry"]
                        }
        except Exception as e:
            print(f"Error fetching route: {e}")
        return None

    async def get_location_address(self, lat: float, lng: float):
        """Reverse geocoding using Nominatim"""
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lng, "format": "json", "zoom": 18, "addressdetails": 1}
        headers = {"User-Agent": "GoldenHourResponse/1.0"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    return response.json().get("display_name", "Unknown Location")
        except Exception as e:
            print(f"Error resolving address: {e}")
        return "Unknown Location"

maps_service = MapsService()
