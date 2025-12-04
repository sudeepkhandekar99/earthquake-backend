import os
import json
from datetime import datetime, timezone
from typing import List, Dict

import boto3
import httpx

s3 = boto3.client("s3")

QUAKES_BUCKET_NAME = os.environ["QUAKES_BUCKET_NAME"]
USGS_FEED_URL = os.environ["USGS_FEED_URL"]


def lambda_handler(event, context):
    # Fetch latest earthquakes from USGS
    resp = httpx.get(USGS_FEED_URL, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()

    # Timestamped key like: raw/20251203T033000Z.json
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key_raw = f"raw/{now}.json"

    # MVP: store the raw feed
    s3.put_object(
        Bucket=QUAKES_BUCKET_NAME,
        Key=key_raw,
        Body=json.dumps(data).encode("utf-8"),
        ContentType="application/json",
    )

    curated = build_curated(data)
    key_curated = f"curated/{now}.json"

    s3.put_object(
        Bucket=QUAKES_BUCKET_NAME,
        Key=key_curated,
        Body=json.dumps(curated).encode("utf-8"),
        ContentType="application/json",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"stored": key_raw}),
    }


def build_curated(data: dict) -> List[Dict]:
    features = data.get("features", [])
    curated = []

    for f in features:
        props = f.get("properties", {})
        geom = f.get("geometry", {}) or {}
        coords = geom.get("coordinates", [None, None, None])

        mag = props.get("mag")
        place = props.get("place")
        time = props.get("time")  # ms since epoch
        quake_id = f.get("id")

        # Simple mag banding
        if mag is None:
            mag_band = "unknown"
        elif mag < 2.5:
            mag_band = "micro"
        elif mag < 4.5:
            mag_band = "light"
        elif mag < 6.0:
            mag_band = "moderate"
        else:
            mag_band = "strong"

        curated.append(
            {
                "id": quake_id,
                "time": time,
                "mag": mag,
                "mag_band": mag_band,
                "place": place,
                "lat": coords[1],
                "lon": coords[0],
                "depth_km": coords[2],
            }
        )

    return curated