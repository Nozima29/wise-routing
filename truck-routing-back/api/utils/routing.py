
import requests

from django.conf import settings


class RoutingError(Exception):
    pass


class TomTomRoutingService:

    BASE_URL = (
        "https://api.tomtom.com/routing/1/calculateRoute"
    )

    def get_routes(
        self,
        origin: dict,
        destination: dict,
        departure_time,
    ) -> list:

        locations = (
            f"{origin['latitude']},{origin['longitude']}:"
            f"{destination['latitude']},{destination['longitude']}"
        )

        url = f"{self.BASE_URL}/{locations}/json"

        params = {
            "key": settings.TOMTOM_API_KEY,
            "maxAlternatives": 2,
            "routeType": "fastest",
            "traffic": "true",
            "travelMode": "truck",
            "departAt": departure_time.isoformat(),
            "routeRepresentation": "polyline",
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

        except requests.RequestException as exc:
            raise RoutingError(
                f"TomTom routing failed: {exc}"
            ) from exc

        routes = data.get("routes", [])

        if not routes:
            raise RoutingError("TomTom returned no routes.")

        return [
            self._parse_route(route, index)
            for index, route in enumerate(routes[:3], start=1)
        ]

    @staticmethod
    def _parse_route(route: dict, alternative_number: int) -> dict:

        summary = route["summary"]

        # TomTom returns route points as latitude/longitude.
        # GeoJSON requires longitude/latitude.
        coordinates = []

        for leg in route.get("legs", []):
            for point in leg.get("points", []):
                coordinates.append([
                    point["longitude"],
                    point["latitude"],
                ])

        if len(coordinates) < 2:
            raise RoutingError(
                f"Route {alternative_number} has invalid geometry."
            )

        return {
            "alternative_number": alternative_number,
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates,
            },
            "distance_miles": (
                summary["lengthInMeters"] / 1609.344
            ),
            "duration_seconds": summary["travelTimeInSeconds"],
        }
