
from rest_framework import serializers
from .models import Trip, Route, Checkpoint


class CheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkpoint
        fields = "__all__"
        read_only_fields = ["id"]


class RouteSerializer(serializers.ModelSerializer):
    checkpoints = CheckpointSerializer(many=True, read_only=True)
    duration_hours = serializers.ReadOnlyField()

    class Meta:
        model = Route
        fields = [
            "id",
            "trip",
            "alternative_number",
            "provider",
            "geometry",
            "distance_miles",
            "duration_seconds",
            "duration_hours",
            "severe_miles",
            "high_miles",
            "average_risk",
            "overall_risk",
            "is_recommended",
            "is_no_travel",
            "checkpoints",
        ]
        read_only_fields = fields


class TripSerializer(serializers.ModelSerializer):
    routes = RouteSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "origin",
            "destination",
            "origin_lat",
            "origin_lon",
            "destination_lat",
            "destination_lon",
            "departure_time",
            "load_weight_lb",
            "checkpoint_interval_miles",
            "status",
            "created_at",
            "updated_at",
            "routes",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
            "routes",
        ]
