from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from api.models import Trip, Status, Route, Checkpoint
from api.serializers import TripSerializer, RouteSerializer, CheckpointSerializer
from api.utils.planner import (
    TripPlanningService,
    TripPlanningError,
)
from api.utils.risk import *
from api.utils.heatmap import *
from api.utils.weather import * 

from datetime import timedelta


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    queryset = Trip.objects.all()
    permission_classes = [AllowAny]

    @action(detail=True, methods=["post"])
    def plan(self, request, pk=None):

        trip = self.get_object()

        if trip.status == Status.PROCESSING:
            return Response(
                {"detail": "Trip is already processing."},
                status=status.HTTP_409_CONFLICT,
            )

        trip.status = Status.PROCESSING
        trip.save(update_fields=["status", "updated_at"])

        try:
            service = TripPlanningService()
            service.plan(trip)

            return Response(
                TripSerializer(trip).data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            trip.status = Status.FAILED
            trip.save(update_fields=["status", "updated_at"])

            return Response(
                {
                    "status": "failed",
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=True, methods=["get"])
    def heatmap(self, request, pk=None):
        trip = self.get_object()

        try:
            offset_hours = int(request.query_params.get("offset_hours", 0))
        except (TypeError, ValueError):
            return Response(
                {"detail": "offset_hours must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not 0 <= offset_hours <= 48:
            return Response(
                {"detail": "offset_hours must be between 0 and 48."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        route_id = request.query_params.get("route_id")

        routes = trip.routes.all()

        if route_id:
            route = routes.filter(id=route_id).first()
        else:
            route = routes.filter(is_recommended=True).first()
            if route is None:
                route = routes.first()

        if route is None:
            return Response(
                {"detail": "No route found for this trip."},
                status=status.HTTP_404_NOT_FOUND,
            )

        forecast_time = trip.departure_time + timedelta(
            hours=offset_hours
        )

        try:
            points = sample_route(route.geometry, interval_miles=5)

            weather_service = OpenMeteoService()
            weather_data = weather_service.get_weather_at_time(
                points,
                forecast_time,
            )

            heatmap_points = []

            for point, weather in zip(points, weather_data):
                risk = calculate_checkpoint_risk(
                    weather,
                    trip.load_weight_lb,
                )

                heatmap_points.append({
                    **point,
                    **weather,
                    "risk_level": risk.level,
                    "risk_score": risk.score,
                    "risk_reason": risk.reason,
                })

        except Exception:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Failed to generate trip heatmap")

            return Response(
                {"detail": "Unable to retrieve heatmap weather data."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            "trip_id": trip.id,
            "route_id": route.id,
            "offset_hours": offset_hours,
            "forecast_time": forecast_time.isoformat(),
            "interval_miles": 5,
            "points": heatmap_points,
        })

class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RouteSerializer
    queryset = Route.objects.prefetch_related("checkpoints").all()


class CheckpointViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CheckpointSerializer
    queryset = Checkpoint.objects.all()