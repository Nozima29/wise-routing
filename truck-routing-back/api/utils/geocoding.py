
import requests

from django.core.cache import cache
from django.conf import settings


class GeocodingError(Exception):
    pass


class NominatimService:

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def geocode(self, address: str) -> dict:
        cache_key = f"geocode:{address.strip().lower()}"

        cached = cache.get(cache_key)

        if cached:
            return cached

        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    "q": address,
                    "format": "jsonv2",
                    "limit": 1,
                },
                headers={
                    "User-Agent": settings.NOMINATIM_USER_AGENT,
                },
                timeout=15,
            )

            response.raise_for_status()
            results = response.json()

        except requests.RequestException as exc:
            raise GeocodingError(
                f"Geocoding request failed: {exc}"
            ) from exc

        if not results:
            raise GeocodingError(
                f"Address not found: {address}"
            )

        result = {
            "latitude": float(results[0]["lat"]),
            "longitude": float(results[0]["lon"]),
            "display_name": results[0]["display_name"],
        }

        cache.set(cache_key, result, timeout=60 * 60 * 24 * 30)

        return result
