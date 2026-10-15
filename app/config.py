import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'cityinsight.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEATHER_FRESHNESS_MINUTES = int(os.getenv("WEATHER_FRESHNESS_MINUTES", "15"))
