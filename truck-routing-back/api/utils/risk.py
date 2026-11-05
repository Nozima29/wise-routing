
from dataclasses import dataclass
from typing import Optional


RISK_SCORES = {
    "low": 1,
    "moderate": 2,
    "high": 3,
    "severe": 4,
    "no_travel": 5,
}

RISK_ORDER = {
    "low": 1,
    "moderate": 2,
    "high": 3,
    "severe": 4,
    "no_travel": 5,
}


class RiskCalculationError(Exception):
    pass


@dataclass
class CheckpointRisk:
    level: str
    score: int
    reason: str


def classify_wind(wind_mph: float) -> str:
    if wind_mph >= 55:
        return "no_travel"
    if wind_mph >= 45:
        return "severe"
    if wind_mph >= 35:
        return "high"
    if wind_mph >= 25:
        return "moderate"
    return "low"


def classify_rain(rain_in_per_hour: float) -> str:
    if rain_in_per_hour > 1.00:
        return "no_travel"
    if rain_in_per_hour >= 0.50:
        return "severe"
    if rain_in_per_hour >= 0.25:
        return "high"
    if rain_in_per_hour >= 0.10:
        return "moderate"
    return "low"


def classify_snow(snow_in_per_hour: float) -> str:
    if snow_in_per_hour > 3.00:
        return "no_travel"
    if snow_in_per_hour >= 2.00:
        return "severe"
    if snow_in_per_hour >= 1.00:
        return "high"
    if snow_in_per_hour >= 0.50:
        return "moderate"
    return "low"


def calculate_checkpoint_risk(
    weather: dict,
    load_weight_lb: float,
) -> CheckpointRisk:
    """
    Calculate checkpoint risk using the assignment's weather
    thresholds and truck-load rules.
    """

    required_fields = {
        "wind_speed_mph": weather.get("wind_speed_mph", 0.0),
        "precipitation_in_per_hour": weather.get(
            "precipitation_in_per_hour"
        ),
        "snowfall_in_per_hour": weather.get(
            "snowfall_in_per_hour"
        ),
    }

    missing_fields = [
        name for name, value in required_fields.items()
        if value is None
    ]

    if missing_fields:
        raise RiskCalculationError(
            f"Missing weather values: {', '.join(missing_fields)}"
        )

    wind = float(required_fields["wind_speed_mph"])
    rain = float(required_fields["precipitation_in_per_hour"])
    snow = float(required_fields["snowfall_in_per_hour"])

    if load_weight_lb < 0:
        raise RiskCalculationError("Load weight cannot be negative.")

    wind_risk = classify_wind(wind)
    rain_risk = classify_rain(rain)
    snow_risk = classify_snow(snow)

    conditions = [
        ("Wind", wind_risk),
        ("Rain", rain_risk),
        ("Snow", snow_risk),
    ]

    reasons = [
        f"{name}: {level.replace('_', ' ').title()}"
        for name, level in conditions
        if level != "low"
    ]

    # Apply the assignment's additional truck-load rules.
    if wind >= 55:
        conditions.append(("Load rule", "no_travel"))
        reasons.append("Wind >= 55 mph: no travel for any load")

    elif wind >= 45 and load_weight_lb > 30000:
        conditions.append(("Load rule", "no_travel"))
        reasons.append(
            "Wind 45–54 mph with load above 30,000 lb: no travel"
        )

    elif wind >= 35 and load_weight_lb > 40000:
        conditions.append(("Load rule", "severe"))
        reasons.append(
            "Wind 35–44 mph with load above 40,000 lb: severe risk"
        )

    highest_risk = max(
        (level for _, level in conditions),
        key=lambda level: RISK_ORDER[level],
    )

    if not reasons:
        reasons.append("All measured weather conditions are low risk")

    return CheckpointRisk(
        level=highest_risk,
        score=RISK_SCORES[highest_risk],
        reason="; ".join(reasons),
    )


def evaluate_route(
    checkpoints: list,
    weather_data: list,
    load_weight_lb: float,
) -> dict:
    """
    Calculate checkpoint risks and aggregate route metrics.

    A checkpoint's risk represents the road segment from that
    checkpoint to the next checkpoint.
    """

    if len(checkpoints) != len(weather_data):
        raise RiskCalculationError(
            "Checkpoint and weather data counts do not match."
        )

    if not checkpoints:
        raise RiskCalculationError("Route has no checkpoints.")

    evaluated_checkpoints = []

    for checkpoint, weather in zip(checkpoints, weather_data):
        risk = calculate_checkpoint_risk(
            weather,
            load_weight_lb,
        )

        evaluated_checkpoints.append({
            **checkpoint,
            **weather,
            "risk_level": risk.level,
            "risk_score": risk.score,
            "risk_reason": risk.reason,
        })

    severe_miles = 0.0
    high_miles = 0.0
    weighted_risk = 0.0
    total_segment_miles = 0.0

    for index, checkpoint in enumerate(evaluated_checkpoints[:-1]):
        next_checkpoint = evaluated_checkpoints[index + 1]

        segment_miles = (
            next_checkpoint["distance_from_origin_miles"]
            - checkpoint["distance_from_origin_miles"]
        )

        if segment_miles < 0:
            raise RiskCalculationError(
                "Checkpoint distances must be in ascending order."
            )

        level = checkpoint["risk_level"]

        if level == "severe":
            severe_miles += segment_miles
        elif level == "high":
            high_miles += segment_miles

        weighted_risk += checkpoint["risk_score"] * segment_miles
        total_segment_miles += segment_miles

    average_risk = (
        weighted_risk / total_segment_miles
        if total_segment_miles > 0
        else evaluated_checkpoints[0]["risk_score"]
    )

    overall_risk = max(
        evaluated_checkpoints,
        key=lambda cp: cp["risk_score"],
    )["risk_level"]

    is_no_travel = any(
        cp["risk_level"] == "no_travel"
        for cp in evaluated_checkpoints
    )

    return {
        "checkpoints": evaluated_checkpoints,
        "severe_miles": round(severe_miles, 2),
        "high_miles": round(high_miles, 2),
        "average_risk": round(average_risk, 3),
        "overall_risk": overall_risk,
        "is_no_travel": is_no_travel,
    }


def recommend_routes(route_metrics: list) -> Optional[int]:
    """
    Return the index of the recommended route.

    Routes with No Travel conditions are excluded. If all routes
    have No Travel conditions, no route is recommended.
    """

    eligible = [
        (index, route)
        for index, route in enumerate(route_metrics)
        if not route["is_no_travel"]
    ]

    if not eligible:
        return None

    recommended_index, _ = min(
        eligible,
        key=lambda item: (
            item[1]["severe_miles"],
            item[1]["high_miles"],
            item[1]["average_risk"],
            item[1]["duration_seconds"],
        ),
    )

    return recommended_index
