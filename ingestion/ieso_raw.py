"""Download the  IESO public reports and land them untouched in object storage."""

import hashlib
import os
import time
from datetime import date

import boto3
import requests
from botocore.client import Config
from botocore.exceptions import ClientError

BASE_URL = "https://reports-public.ieso.ca/public"


def report_url(report: str, filename: str) -> str:
    return f"{BASE_URL}/{report}/{filename}"


def download(url: str, timeout: int = 120, attempts: int = 3) -> bytes:
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            body = response.content
            break
        except (
            requests.ConnectionError,
            requests.Timeout,
            requests.exceptions.ChunkedEncodingError,
        ):
            if attempt == attempts:
                raise
            time.sleep(5 * attempt)

    if not body:
        raise ValueError(f"Empty response from {url}")
    start = body[:300].lstrip().lower()
    if start.startswith((b"<html", b"<!doctype html")):
        raise ValueError(f"Got an HTML page instead of a report from {url}")
    return body


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL", "http://localhost:9000"),
        aws_access_key_id=os.getenv("RUSTFS_ACCESS_KEY", "rustfsadmin"),
        aws_secret_access_key=os.getenv("RUSTFS_SECRET_KEY", "rustfsadmin_secret"),
        region_name="us-east-1",
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def ensure_bucket(s3, bucket: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError:
        s3.create_bucket(Bucket=bucket)


def raw_key(report: str, filename: str, ingest_date: date) -> str:
    return f"ieso/{report}/ingest_date={ingest_date:%Y-%m-%d}/{filename}"


def land_raw(s3, bucket: str, report: str, filename: str, ingest_date: date, body: bytes) -> str:
    key = raw_key(report, filename, ingest_date)
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        Metadata={"sha256": hashlib.sha256(body).hexdigest()},
    )
    return key


def ingest_report(
    report: str, filename: str, ingest_date: date, bucket: str = "raw", s3=None
) -> str:
    s3 = s3 or s3_client()
    ensure_bucket(s3, bucket)
    body = download(report_url(report, filename))
    return land_raw(s3, bucket, report, filename, ingest_date, body)
