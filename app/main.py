import os
from collections import Counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .storage import get_latest_raw, get_latest_curated

app = FastAPI(
    title="Earthquake Backend",
    description="Serverless FastAPI backend for real-time earthquake analytics.",
    version="0.1.0",
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """
    Simple health check endpoint.
    Also echoes which bucket + feed URL the backend is using.
    """
    return {
        "status": "ok",
        "quakes_bucket": os.getenv("QUAKES_BUCKET_NAME"),
        "usgs_feed_url": os.getenv("USGS_FEED_URL"),
    }


@app.get("/earthquakes/latest")
async def latest():
    """
    Returns the latest raw USGS GeoJSON feed stored in S3.
    """
    data = get_latest_raw()
    if not data:
        raise HTTPException(status_code=404, detail="No data yet")
    return data


@app.get("/earthquakes/summary")
async def summary():
    """
    Returns a curated list of earthquakes from the latest snapshot.
    Each item is a slim object with id, mag, mag_band, place, lat/lon, etc.
    """
    data = get_latest_curated()
    if not data:
        raise HTTPException(status_code=404, detail="No curated data yet")
    return data


@app.get("/earthquakes/stats")
async def stats():
    """
    Returns basic stats computed from the latest curated snapshot.
    """
    curated = get_latest_curated()
    if not curated:
        raise HTTPException(status_code=404, detail="No curated data yet")

    mag_bands = Counter(item.get("mag_band", "unknown") for item in curated)
    max_mag = max((item.get("mag") or 0) for item in curated) if curated else 0
    total = len(curated)

    return {
        "total_events": total,
        "max_magnitude": max_mag,
        "count_by_mag_band": dict(mag_bands),
    }


# Lambda entrypoint for API Gateway
handler = Mangum(app)