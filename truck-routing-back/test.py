import requests


def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"

    response = requests.get(
        url,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m"
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max"
            ],
            "timezone": "Asia/Tashkent"
        }
    )

    print(response.json())

def get_routes():
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        "69.2401,41.2995;69.2797,41.3111"
    )

    response = requests.get(
        url,
        params={"overview": "false"}
    )

    data = response.json()

    route = data["routes"][0]

    print("Distance:", route["distance"] / 1000, "km")
    print("Duration:", route["duration"] / 60, "minutes")


def get_geocode():    
    url = "https://nominatim.openstreetmap.org/search"

    response = requests.get(
        url,
        params={
            "q": "Chilanzar 1, Tashkent",
            "format": "json",
            "limit": 1
        },
        headers={
            "User-Agent": "MyLocationApp/1.0"
        }
    )

    lat = response.json()[0].get('lat')
    lon = response.json()[0].get('lon')
    return lat, lon

#get_routes()
lat, lon = get_geocode()
get_weather(lat, lon)