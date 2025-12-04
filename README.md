# 🌍 Earthquake Backend – Serverless Real-Time Earthquake Analytics

This backend ingests live USGS earthquake data into AWS S3 and exposes API endpoints via FastAPI running inside AWS Lambda.

---

# 🚀 Features

- Scheduled ingestion from **USGS GeoJSON feed**
- Raw + curated datasets stored in **S3**
- Serverless **FastAPI** behind API Gateway
- JSON endpoints for dashboards and analytics
- Fully deployed using **AWS SAM + GitHub Actions**

---

# Architecture Overview

```
USGS Feed → EventBridge (hourly)
          → Ingest Lambda
              → S3/raw/<timestamp>.json
              → S3/curated/<timestamp>.json

API Gateway → FastAPI Lambda → Reads latest from S3
```

Services used:

- **AWS Lambda** – ingestion + API  
- **EventBridge** – triggers ingestion every hour  
- **S3** – durable storage (raw + curated)  
- **SSM Parameter Store** – config values  
- **API Gateway** – public HTTPS endpoints  
- **AWS SAM** – IaC  
- **GitHub Actions** – CI/CD deploy  

---

# Endpoints

### `GET /health`
Returns status + bucket + feed URL.

---

### `GET /earthquakes/latest`
**Returns:**  
The **raw USGS GeoJSON** stored in S3.

Shape (example):

```json
{
  "type": "FeatureCollection",
  "metadata": { "count": 6 },
  "features": [
    {
      "id": "us7000rfg4",
      "properties": { "mag": 5.3, "place": "Mexico" },
      "geometry": { "coordinates": [-95.3963, 16.1043, 62.608] }
    }
  ]
}
```

---

### `GET /earthquakes/summary`
Returns the curated list (one item per earthquake).

Shape:

```json
[
  {
    "id": "us7000rfg4",
    "time": 1764819909690,
    "mag": 5.3,
    "mag_band": "moderate",
    "place": "1 km WNW of El Morro, Mexico",
    "lat": 16.1043,
    "lon": -95.3963,
    "depth_km": 62.608
  }
]
```

---

### `GET /earthquakes/stats`
Aggregate statistics from curated data.

Shape:

```json
{
  "total_events": 9,
  "max_magnitude": 5.3,
  "count_by_mag_band": {
    "micro": 7,
    "light": 1,
    "moderate": 1
  }
}
```

---

# Ingestion Pipeline

Code: `app/ingest.py`

### Steps

1. EventBridge triggers `IngestFunction` every hour.
2. Lambda fetches USGS GeoJSON:

```python
resp = httpx.get(USGS_FEED_URL)
data = resp.json()
```

3. Store **raw**:

```
s3://<bucket>/raw/<timestamp>.json
```

4. Build curated list (slim per-earthquake items).
5. Store curated:

```
s3://<bucket>/curated/<timestamp>.json
```

---

# S3 Structure

```
raw/
    20251203T020000Z.json
    20251203T030000Z.json
curated/
    20251203T020000Z.json
    20251203T030000Z.json
```

---

# 🛠 Local Development

Run FastAPI locally:

```bash
uvicorn app.main:app --reload
```

Optional: Set environment variables:

```bash
export QUAKES_BUCKET_NAME=yourbucket
export USGS_FEED_URL=https://earthquake.usgs.gov/...
```

---

# Deployment (CI/CD via GitHub Actions)

GitHub Actions workflow builds + deploys SAM template:

- Installs SAM CLI  
- Runs:

```bash
sam build
sam deploy --stack-name earthquake-backend-dev ...
```

Output includes API Gateway URL:

```
https://<api-id>.execute-api.<region>.amazonaws.com/Prod/
```

---

# 🎉 Status

Backend is fully functional:

- Raw + curated data landing correctly  
- All API endpoints working  
- IAM permissions correctly configured  
- CORS enabled for frontend  
- Ready for dashboard UI  