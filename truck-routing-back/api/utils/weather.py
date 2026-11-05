
import requests

from datetime import timezone, datetime
from math import isfinite


class WeatherError(Exception):
    pass


class OpenMeteoService:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    HOURLY_VARIABLES = [
        "temperature_2m",
        "wind_speed_10m",
        "rain",
        "snowfall",
        "visibility",
    ]

    def get_weather(self, checkpoints: list) -> list:
        """
        Retrieve forecasts in batches of 20 coordinates.

        Returns weather matched to each checkpoint's ETA.
        """

        results = []

        batch_size = 20

        for start in range(0, len(checkpoints), batch_size):
            batch = checkpoints[start:start + batch_size]

            params = {
                "latitude": ",".join(
                    str(cp["latitude"]) for cp in batch
                ),
                "longitude": ",".join(
                    str(cp["longitude"]) for cp in batch
                ),
                "hourly": ",".join(self.HOURLY_VARIABLES),
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
                "timezone": "UTC",
                "forecast_days": 7,
            }

            try:
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

            except requests.RequestException as exc:
                raise WeatherError(
                    f"Open-Meteo request failed: {exc}"
                ) from exc

            # Multiple locations return a list of responses.
            if len(batch) == 1:
                locations = [data]
            else:
                locations = data

            if not isinstance(locations, list):
                raise WeatherError(
                    "Unexpected Open-Meteo response."
                )

            if len(locations) != len(batch):
                raise WeatherError(
                    "Weather response count does not match checkpoints."
                )

            for checkpoint, location_data in zip(
                batch, locations
            ):
                results.append(
                    self._match_forecast(
                        checkpoint,
                        location_data,
                    )
                )

        return results

    def get_weather_at_time(self, points, forecast_time: datetime):
        """
        Retrieve weather at one selected timestamp for all route points.

        Reuses the existing batching and forecast matching logic.
        """
        timed_points = [
            {
                **point,
                "estimated_arrival": forecast_time,
            }
            for point in points
        ]

        return self.get_weather(timed_points)

    def _match_forecast(self, checkpoint, data):
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        if not times:
            raise WeatherError("No hourly forecast returned.")

        eta = checkpoint["estimated_arrival"].astimezone(
            timezone.utc
        )

        # Find the nearest available forecast hour.
        index = min(
            range(len(times)),
            key=lambda i: abs(
                (
                    self._parse_time(times[i]) - eta
                ).total_seconds()
            ),
        )

        forecast_time = self._parse_time(times[index])

        if abs((forecast_time - eta).total_seconds()) > 3600:
            raise WeatherError(
                f"No suitable hourly forecast for {eta.isoformat()}"
            )

        units = data.get("hourly_units", {})

        def get_value(name):
            values = hourly.get(name, [])

            if index >= len(values) or values[index] is None:
                return None

            value = float(values[index])

            if not isfinite(value):
                return None

            return value

        temperature = get_value("temperature_2m")
        wind = get_value("wind_speed_10m")
        rain = get_value("rain")
        snow = get_value("snowfall")
        visibility = get_value("visibility")

        # Normalize snowfall to inches.
        snow_unit = units.get("snowfall", "")

        if snow is not None and snow_unit == "cm":
            snow /= 2.54
        elif snow is not None and snow_unit == "mm":
            snow /= 25.4

        # Normalize visibility to miles.
        visibility_unit = units.get("visibility", "")

        if visibility is not None and visibility_unit == "m":
            visibility /= 1609.344
        elif visibility is not None and visibility_unit == "km":
            visibility /= 1.609344

        return {
            "temperature_f": temperature,
            "wind_speed_mph": wind,
            "precipitation_in_per_hour": rain,
            "snowfall_in_per_hour": snow,
            "visibility_miles": visibility,
            "forecast_time": forecast_time,
        }

    @staticmethod
    def _parse_time(value):
        from datetime import datetime

        return datetime.fromisoformat(
            value
        ).replace(tzinfo=timezone.utc)
