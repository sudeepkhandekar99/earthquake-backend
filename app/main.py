import os
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()


@app.get("/health")
async def health():
    """
    Simple health check endpoint.
    """
    return {
        "status": "ok",
        "quakes_bucket": os.getenv("QUAKES_BUCKET_NAME"),
        "usgs_feed_url": os.getenv("USGS_FEED_URL"),
    }


# Lambda handler for API Gateway
handler = Mangum(app)