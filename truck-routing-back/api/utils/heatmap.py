import math

EARTH_RADIUS_MILES = 3958.7613


def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(
        math.radians,
        [lon1, lat1, lon2, lat2],
    )

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


def interpolate_point(start, end, fraction):
    return (
        start[0] + (end[0] - start[0]) * fraction,
        start[1] + (end[1] - start[1]) * fraction,
    )


def sample_route(geometry, interval_miles=5):
    """
    Sample a GeoJSON LineString at regular distance intervals.

    Coordinates are stored as [longitude, latitude].
    """

    if interval_miles <= 0:
        raise ValueError("Sampling interval must be positive.")

    coordinates = geometry.get("coordinates", [])

    if len(coordinates) < 2:
        raise ValueError("Route geometry is invalid.")

    segments = []
    total_distance = 0.0

    for start, end in zip(coordinates[:-1], coordinates[1:]):
        distance = haversine(
            start[0], start[1],
            end[0], end[1],
        )

        if distance <= 0:
            continue

        segments.append({
            "start": start,
            "end": end,
            "distance": distance,
            "start_distance": total_distance,
        })

        total_distance += distance

    if total_distance <= 0:
        raise ValueError("Route has no measurable distance.")

    target_distances = []
    current = 0.0
    lon, lat = 0, 0
    
    while current < total_distance:
        target_distances.append(current)
        current += interval_miles

    # Always include the route destination.
    target_distances.append(total_distance)

    points = []

    for sequence, target in enumerate(target_distances):
        if target >= total_distance:
            lon, lat = coordinates[-1]
        else:
            for segment in segments:
                segment_end = (
                    segment["start_distance"] + segment["distance"]
                )

                if target <= segment_end:
                    fraction = (
                        target - segment["start_distance"]
                    ) / segment["distance"]

                    lon, lat = interpolate_point(
                        segment["start"],
                        segment["end"],
                        fraction,
                    )
                    break

        points.append({
            "sequence": sequence,
            "distance_from_origin_miles": round(target, 2),
            "latitude": lat,
            "longitude": lon,
        })

    return points