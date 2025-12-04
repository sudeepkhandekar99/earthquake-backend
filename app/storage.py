import os
import json

import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["QUAKES_BUCKET_NAME"]


def get_latest_raw():
    """
    Returns the JSON from the latest object under raw/ in the quake bucket.
    If no objects exist, returns None.
    """
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix="raw/")
    contents = resp.get("Contents", [])
    if not contents:
        return None

    # Pick the most recently modified object
    latest = max(contents, key=lambda x: x["LastModified"])
    obj = s3.get_object(Bucket=BUCKET, Key=latest["Key"])
    body = obj["Body"].read().decode("utf-8")
    return json.loads(body)