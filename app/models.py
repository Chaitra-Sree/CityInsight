from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    country = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class WeatherReading(db.Model):
    __tablename__ = "weather_readings"

    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    temperature_c = db.Column(db.Float, nullable=False)
    windspeed_kmh = db.Column(db.Float)
    weather_code = db.Column(db.Integer)
    fetched_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    city = db.relationship("City", backref="weather_readings")

    __table_args__ = (
        db.Index("ix_weather_city_fetched", "city_id", "fetched_at"),
    )
