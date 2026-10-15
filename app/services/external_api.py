import requests


BASE_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
BASE_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


class ExternalAPIError(RuntimeError):
    pass


def geocode_city(name):
    try:
        response = requests.get(
            BASE_GEOCODING_URL,
            params={"name": name, "count": 1, "language": "en", "format": "json"},
            timeout=8,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
    except (requests.RequestException, ValueError) as exc:
        raise ExternalAPIError("The location service is temporarily unavailable.") from exc

    if not results:
        return None
    place = results[0]
    return {
        "name": place["name"],
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "country": place.get("country", "Unknown"),
    }


def fetch_weather(latitude, longitude):
    try:
        response = requests.get(
            BASE_WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m,weather_code",
                "timezone": "auto",
            },
            timeout=8,
        )
        response.raise_for_status()
        current = response.json()["current"]
    except (requests.RequestException, ValueError, KeyError) as exc:
        raise ExternalAPIError("The weather service is temporarily unavailable.") from exc

    return {
        "temperature_c": current["temperature_2m"],
        "windspeed_kmh": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
    }
