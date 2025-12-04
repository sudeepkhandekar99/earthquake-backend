import os
import json

import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["QUAKES_BUCKET_NAME"]


def _get_latest_key(prefix: str) -> str | None:
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    contents = resp.get("Contents", [])
    if not contents:
        return None
    latest = max(contents, key=lambda x: x["LastModified"])
    return latest["Key"]


def get_latest_raw():
    key = _get_latest_key("raw/")
    if not key:
        return None
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return json.loads(obj["Body"].read().decode("utf-8"))


def get_latest_curated():
    key = _get_latest_key("curated/")
    if not key:
        return None
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return json.loads(obj["Body"].read().decode("utf-8"))