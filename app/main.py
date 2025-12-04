import os
from collections import Counter

from fastapi import FastAPI, HTTPException
from mangum import Mangum

from .storage import get_latest_raw, get_latest_curated

app = FastAPI()


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "quakes_bucket": os.getenv("QUAKES_BUCKET_NAME"),
        "usgs_feed_url": os.getenv("USGS_FEED_URL"),
    }


@app.get("/earthquakes/latest")
async def latest():
    data = get_latest_raw()
    if not data:
        raise HTTPException(status_code=404, detail="No data yet")
    return data


@app.get("/earthquakes/summary")
async def summary():
    """
    Returns the curated list (one item per quake with slimmed fields).
    """
    data = get_latest_curated()
    if not data:
        raise HTTPException(status_code=404, detail="No curated data yet")
    return data


@app.get("/earthquakes/stats")
async def stats():
    """
    Returns basic stats computed from the curated list.
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
        "count_by_mag_band": mag_bands,
    }


handler = Mangum(app)