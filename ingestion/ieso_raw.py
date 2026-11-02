""" Download the  IESO public reports and land them untouched in object storage."""

import requests

BASE_URL = "https://reports-public.ieso.ca/public"

def report_url(report:str , filename:str) -> str:
    return f"{BASE_URL}/{report}/{filename}"

def download(url:str, timeout: int=120) -> bytes:
    response = requests.get(url,timeout = timeout)
    response.raise_for_status()
    body = response.content
    if not body:
        raise ValueError(f"Empty response form {url}")
    start = body[:300].lstrip().lower()
    if start.startswith(b"<html") or start.startswith(b"<!doctype html"):
        raise ValueError(f"Got an HTML page instead of a report from {url}")
    return body