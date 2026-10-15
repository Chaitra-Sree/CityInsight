from datetime import datetime, timedelta, timezone
from unittest import result

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import func

from .models import City, WeatherReading, db
from .services.external_api import ExternalAPIError, fetch_weather, geocode_city


bp = Blueprint("main", __name__)


def utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def serialize(city, reading=None, source=None):
    result = {
        "id": city.id,
        "name": city.name,
        "country": city.country,
        "latitude": city.latitude,
        "longitude": city.longitude,
        "weather": None,
    }
    if reading:
        result["weather"] = {
            "temperature_c": reading.temperature_c,
            "windspeed_kmh": reading.windspeed_kmh,
            "weather_code": getattr(reading, "weather_code", None),
            "fetched_at": reading.fetched_at.isoformat() + "Z",
            "source": source,
        }
    return result


@bp.get("/")
def dashboard():
    return render_template("index.html")


@bp.post("/cities")
def add_city():
    payload = request.get_json(silent=True) or {}
    name = " ".join(str(payload.get("name", "")).split())
    if not name or len(name) > 120:
        return jsonify(error="Enter a valid city name."), 400

    existing = City.query.filter(func.lower(City.name) == name.lower()).first()
    if existing:
        result = serialize(existing)
        result["message"] = "City already exists."
        return jsonify(result), 200

    try:
        place = geocode_city(name)
    except ExternalAPIError as exc:
        return jsonify(error=str(exc)), 503
    if not place:
        return jsonify(error="City not found. Check the spelling and try again."), 404

    city = City(**place)
    db.session.add(city)
    db.session.commit()
    result = serialize(city)
    result["message"] = "City added successfully."
    return jsonify(result), 201


@bp.get("/cities")
def list_cities():
    cities = City.query.order_by(City.name).all()
    if not cities:
        return jsonify([])

    latest = (
        db.session.query(
            WeatherReading.city_id, func.max(WeatherReading.fetched_at).label("latest")
        )
        .filter(WeatherReading.city_id.in_([city.id for city in cities]))
        .group_by(WeatherReading.city_id)
        .subquery()
    )
    readings = (
        WeatherReading.query.join(
            latest,
            (WeatherReading.city_id == latest.c.city_id)
            & (WeatherReading.fetched_at == latest.c.latest),
        ).all()
    )
    reading_by_city = {reading.city_id: reading for reading in readings}
    return jsonify([serialize(city, reading_by_city.get(city.id), "database") for city in cities])


@bp.get("/cities/<string:name>/weather")
def city_weather(name):
    city = City.query.filter(func.lower(City.name) == name.lower()).first()
    if not city:
        return jsonify(error="City is not in your dashboard yet."), 404

    latest = (
        WeatherReading.query.filter_by(city_id=city.id)
        .order_by(WeatherReading.fetched_at.desc())
        .first()
    )
    from flask import current_app
    cutoff = utcnow_naive() - timedelta(minutes=current_app.config["WEATHER_FRESHNESS_MINUTES"])
    if latest and latest.fetched_at >= cutoff:
        return jsonify(serialize(city, latest, "database cache"))

    try:
        weather = fetch_weather(city.latitude, city.longitude)
    except ExternalAPIError as exc:
        if latest:
            return jsonify(serialize(city, latest, "stale database cache")), 200
        return jsonify(error=str(exc)), 503

    reading = WeatherReading(city_id=city.id, fetched_at=utcnow_naive(), **weather)
    db.session.add(reading)
    db.session.commit()
    return jsonify(serialize(city, reading, "Open-Meteo API"))


@bp.delete("/cities/<int:city_id>")
def delete_city(city_id):
    city = db.session.get(City, city_id)
    if not city:
        return jsonify(error="City not found."), 404
    WeatherReading.query.filter_by(city_id=city.id).delete()
    db.session.delete(city)
    db.session.commit()
    return jsonify(message="City removed.")
