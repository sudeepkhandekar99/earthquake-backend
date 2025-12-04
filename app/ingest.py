import os
import json
from datetime import datetime, timezone

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

    return {
        "statusCode": 200,
        "body": json.dumps({"stored": key_raw}),
    }