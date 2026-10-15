import pytest

from app import create_app
from app.models import db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEATHER_FRESHNESS_MINUTES = 15


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CityInsight" in response.data


def test_add_and_fetch_city(client, monkeypatch):
    monkeypatch.setattr("app.routes.geocode_city", lambda name: {
        "name": "Hyderabad", "latitude": 17.38, "longitude": 78.48, "country": "India"
    })
    monkeypatch.setattr("app.routes.fetch_weather", lambda lat, lon: {
        "temperature_c": 29, "windspeed_kmh": 10, "weather_code": 1
    })
    response = client.post("/cities", json={"name": "Hyderabad"})
    assert response.status_code == 201
    weather = client.get("/cities/Hyderabad/weather").get_json()
    assert weather["weather"]["temperature_c"] == 29
    assert weather["weather"]["source"] == "Open-Meteo API"


def test_rejects_blank_city(client):
    assert client.post("/cities", json={"name": "  "}).status_code == 400
