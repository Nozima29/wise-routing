
from django.db import models


#Enums
class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"


class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MODERATE = "moderate", "Moderate"
        HIGH = "high", "High"
        SEVERE = "severe", "Severe"
        NO_TRAVEL = "no_travel", "No Travel"


#Models
class Trip(models.Model):
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)

    # Geocoded coordinates
    origin_lat = models.FloatField(null=True, blank=True)
    origin_lon = models.FloatField(null=True, blank=True)

    destination_lat = models.FloatField(null=True, blank=True)
    destination_lon = models.FloatField(null=True, blank=True)

    departure_time = models.DateTimeField()

    load_weight_lb = models.PositiveIntegerField()

    checkpoint_interval_miles = models.PositiveSmallIntegerField(
        choices=[
            (10, "10 miles"),
            (25, "25 miles"),
            (50, "50 miles"),
        ],
        default=25,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.origin} -> {self.destination}"


class Route(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="routes",
    )

    alternative_number = models.PositiveSmallIntegerField()

    provider = models.CharField(
        max_length=50,
        default="tomtom",
    )

    # GeoJSON LineString / MultiLineString
    geometry = models.JSONField(null=True, blank=True)

    distance_miles = models.FloatField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)

    severe_miles = models.FloatField(default=0)
    high_miles = models.FloatField(default=0)
    average_risk = models.FloatField(default=0)

    overall_risk = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
    )

    is_recommended = models.BooleanField(default=False)
    is_no_travel = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["alternative_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "alternative_number"],
                name="unique_route_alternative_per_trip",
            )
        ]

    @property
    def duration_hours(self):
        return round(self.duration_seconds / 3600, 2)

    def __str__(self):
        return f"Route {self.alternative_number} - Trip {self.trip}"


class Checkpoint(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="checkpoints",
    )

    sequence = models.PositiveIntegerField()

    distance_from_origin_miles = models.FloatField()

    latitude = models.FloatField()
    longitude = models.FloatField()

    estimated_arrival = models.DateTimeField()

    # Weather information
    temperature_f = models.FloatField(null=True, blank=True)
    wind_speed_mph = models.FloatField(null=True, blank=True)
    precipitation_in_per_hour = models.FloatField(null=True, blank=True)
    snowfall_in_per_hour = models.FloatField(null=True, blank=True)
    visibility_miles = models.FloatField(null=True, blank=True)

    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
    )

    risk_score = models.FloatField(default=0)

    # Highest-risk condition responsible for classification
    risk_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["route", "sequence"],
                name="unique_checkpoint_sequence_per_route",
            )
        ]

    def __str__(self):
        return f"Checkpoint {self.sequence} - Route {self.route}"
