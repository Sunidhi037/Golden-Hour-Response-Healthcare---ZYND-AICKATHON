from src.services.maps_service import maps_service

class RoutingAgent:
    """Agent to select the optimal hospital based on travel time."""

    async def find_best_hospital(self, emergency_location: tuple, hospitals: list):
        """
        Finds the hospital with the lowest ETA.
        Args:
            emergency_location: (lat, lon)
            hospitals: List of dicts with 'coords': (lat, lon) key
        """
        evaluated_hospitals = []

        for hospital in hospitals:
            # Get route details for each hospital
            route_info = await maps_service.get_route_details(
                emergency_location, 
                hospital["coords"]
            )
            
            if route_info:
                # Add route data to the hospital object
                hospital_data = hospital.copy()
                hospital_data["route_info"] = route_info
                evaluated_hospitals.append(hospital_data)

        # SORT LOGIC: Ascending order of duration (Quickest first)
        evaluated_hospitals.sort(key=lambda x: x["route_info"]["duration_min"])

        if not evaluated_hospitals:
            return None

        # Return the best one (index 0 after sort)
        return evaluated_hospitals[0]

routing_agent = RoutingAgent()
