
from django.db import transaction

from api.models import Trip, Route, Checkpoint, Status

from .geocoding import NominatimService
from .routing import TomTomRoutingService
from .checkpoints import generate_checkpoints
from .weather import OpenMeteoService


class TripPlanningError(Exception):
    pass


class TripPlanningService:

    def __init__(self):
        self.geocoder = NominatimService()
        self.router = TomTomRoutingService()
        self.weather = OpenMeteoService()

    def plan(self, trip: Trip):

        # 1. Geocode addresses
        origin = self.geocoder.geocode(trip.origin)
        destination = self.geocoder.geocode(trip.destination)

        # Save coordinates
        trip.origin_lat = origin["latitude"]
        trip.origin_lon = origin["longitude"]

        trip.destination_lat = destination["latitude"]
        trip.destination_lon = destination["longitude"]

        trip.save(
            update_fields=[
                "origin_lat",
                "origin_lon",
                "destination_lat",
                "destination_lon",
                "updated_at",
            ]
        )

        # 2. Generate route alternatives
        routes = self.router.get_routes(
            origin=origin,
            destination=destination,
            departure_time=trip.departure_time,
        )

        planned_routes = []

        # 3. Generate checkpoints and weather
        for route_data in routes:

            checkpoints = generate_checkpoints(
                route=route_data,
                departure_time=trip.departure_time,
                interval_miles=trip.checkpoint_interval_miles,
            )

            weather_data = self.weather.get_weather(
                checkpoints
            )

            planned_routes.append({
                "route": route_data,
                "checkpoints": checkpoints,
                "weather": weather_data,
            })

        # 4. Persist results
        with transaction.atomic():

            trip.routes.all().delete()

            for item in planned_routes:

                route_data = item["route"]

                route = Route.objects.create(
                    trip=trip,
                    alternative_number=(
                        route_data["alternative_number"]
                    ),
                    provider="tomtom",
                    geometry=route_data["geometry"],
                    distance_miles=route_data["distance_miles"],
                    duration_seconds=route_data["duration_seconds"],
                )

                checkpoint_objects = []

                for checkpoint, weather in zip(
                    item["checkpoints"],
                    item["weather"],
                ):

                    checkpoint_objects.append(
                        Checkpoint(
                            route=route,
                            sequence=checkpoint["sequence"],
                            distance_from_origin_miles=(
                                checkpoint[
                                    "distance_from_origin_miles"
                                ]
                            ),
                            latitude=checkpoint["latitude"],
                            longitude=checkpoint["longitude"],
                            estimated_arrival=(
                                checkpoint["estimated_arrival"]
                            ),
                            temperature_f=weather["temperature_f"],
                            wind_speed_mph=weather["wind_speed_mph"],
                            precipitation_in_per_hour=(
                                weather[
                                    "precipitation_in_per_hour"
                                ]
                            ),
                            snowfall_in_per_hour=(
                                weather["snowfall_in_per_hour"]
                            ),
                            visibility_miles=(
                                weather["visibility_miles"]
                            ),
                        )
                    )

                Checkpoint.objects.bulk_create(
                    checkpoint_objects
                )

            trip.status = Status.COMPLETED
            trip.save(update_fields=["status", "updated_at"])

        return trip
