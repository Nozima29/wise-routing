
import math
from datetime import timedelta


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

    return 2 * EARTH_RADIUS_MILES * math.asin(
        math.sqrt(a)
    )


def interpolate_point(start, end, fraction):
    return (
        start[0] + (end[0] - start[0]) * fraction,
        start[1] + (end[1] - start[1]) * fraction,
    )


def generate_checkpoints(route, departure_time, interval_miles):
    coordinates = route["geometry"]["coordinates"]

    segments = []
    total_distance = 0
    lon, lat = None, None

    for start, end in zip(coordinates[:-1], coordinates[1:]):
        distance = haversine(
            start[0], start[1],
            end[0], end[1],
        )

        if distance == 0:
            continue

        segments.append({
            "start": start,
            "end": end,
            "distance": distance,
            "start_distance": total_distance,
        })

        total_distance += distance

    if not segments:
        raise ValueError("Route has insufficient geometry.")

    total_duration = route["duration_seconds"]

    distances = list(
        range(0, int(total_distance), interval_miles)
    )

    if not distances or distances[-1] != total_distance:
        distances.append(total_distance) # type: ignore

    checkpoints = []

    for sequence, target_distance in enumerate(distances):
        target_distance = float(target_distance)

        if target_distance >= total_distance:
            lon, lat = coordinates[-1]
        else:
            for segment in segments:
                segment_end = (
                    segment["start_distance"]
                    + segment["distance"]
                )

                if target_distance <= segment_end:
                    fraction = (
                        target_distance
                        - segment["start_distance"]
                    ) / segment["distance"]

                    lon, lat = interpolate_point(
                        segment["start"],
                        segment["end"],
                        fraction,
                    )
                    break

        progress = target_distance / total_distance

        eta = departure_time + timedelta(
            seconds=total_duration * progress
        )

        if lat and lon:
            checkpoints.append({
                "sequence": sequence,
                "distance_from_origin_miles": round(
                    target_distance, 2
                ),
                "latitude": lat,
                "longitude": lon,
                "estimated_arrival": eta,
            })

    return checkpoints
