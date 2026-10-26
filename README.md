# CityInsight

CityInsight is an interview-ready Flask project that demonstrates a complete
external API integration: a city is geocoded through Open-Meteo, stored in
SQLite, and its weather is fetched only when the saved reading is older than
15 minutes.

## What the project demonstrates

- **Flask application factory and Blueprint** architecture
- **REST API** with GET, POST, and DELETE endpoints
- **External API integration** with timeouts and friendly error handling
- **SQLAlchemy + SQLite** persistence and indexed lookups
- **Database caching** to reduce repeat API calls
- **Responsive frontend** using semantic HTML, CSS, and vanilla JavaScript
- **Mocked pytest tests** that do not depend on internet access

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open **http://127.0.0.1:5000** in your browser.

On macOS/Linux, activate the environment with `source venv/bin/activate`.

## REST endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | User-friendly weather dashboard |
| POST | `/cities` | Geocode and save a city |
| GET | `/cities` | List saved cities and latest readings |
| GET | `/cities/<name>/weather` | Return cached or live weather |
| DELETE | `/cities/<id>` | Remove a city and its readings |

Example request:

```bash
curl -X POST http://127.0.0.1:5000/cities \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Hyderabad\"}"
```

## Run tests

```bash
pytest -v
```


## Project structure

```text
cityinsight/
├── app/
│   ├── static/css/style.css
│   ├── static/js/app.js
│   ├── templates/index.html
│   ├── services/external_api.py
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   └── routes.py
├── tests/test_routes.py
├── cityinsight.db
├── requirements.txt
└── run.py
```
