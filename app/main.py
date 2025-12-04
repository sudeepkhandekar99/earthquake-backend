import os

from fastapi import FastAPI, HTTPException
from mangum import Mangum

from .storage import get_latest_raw

app = FastAPI()


@app.get("/health")
async def health():
    """
    Simple health check, also returns which bucket and feed we're using.
    """
    return {
        "status": "ok",
        "quakes_bucket": os.getenv("QUAKES_BUCKET_NAME"),
        "usgs_feed_url": os.getenv("USGS_FEED_URL"),
    }


@app.get("/earthquakes/latest")
async def latest():
    """
    Returns the latest raw USGS feed stored in S3.
    """
    data = get_latest_raw()
    if not data:
        raise HTTPException(status_code=404, detail="No data yet")

    # For now, return full raw payload.
    # Later we can slim this down to only the fields we care about.
    return data


handler = Mangum(app)