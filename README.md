# Apartment Price Service

Minimal backend scaffold for an ML service that predicts apartment prices.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Available endpoints

- `GET /`
- `GET /api/v1/health`
- `POST /api/v1/predictions`

## Example request

```json
{
  "MedInc": 8.3252,
  "HouseAge": 41.0,
  "AveRooms": 6.9841,
  "AveBedrms": 1.0238,
  "Population": 322.0,
  "AveOccup": 2.5556,
  "Latitude": 37.88,
  "Longitude": -122.23
}
```
