from django.contrib import admin
from .models import Trip, Route, Checkpoint


class CheckpointInline(admin.TabularInline):
    model = Checkpoint
    extra = 0


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "origin",
        "destination",
        "load_weight_lb",
        "departure_time",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("origin", "destination")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "trip",
        "alternative_number",
        "distance_miles",
        "overall_risk",
        "is_recommended",
        "is_no_travel",
    )
    inlines = [CheckpointInline]


@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "route",
        "sequence",
        "distance_from_origin_miles",
        "estimated_arrival",
        "risk_level",
    )