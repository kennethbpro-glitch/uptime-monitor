#!/usr/bin/env python3
"""
monitor.py
Automated website uptime & response monitor.
- Reads URLs from urls.txt
- Logs results to CSV
- Uploads logs to S3
- Sends SNS alert if a site is down or slow
"""

import os
import time
import csv
import datetime
import requests
import boto3
from botocore.exceptions import ClientError

# CONFIG: replace with environment variables or hardcode (better: env vars)
S3_BUCKET = os.environ.get("S3_BUCKET") or "your-unique-bucket-name"
S3_PREFIX = os.environ.get("S3_PREFIX") or "uptime-logs"
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN") or "arn:aws:sns:us-east-1:123456789012:uptime-alerts"
URLS_FILE = os.environ.get("URLS_FILE") or "urls.txt"
LOG_DIR = os.environ.get("LOG_DIR") or "./logs"
THRESHOLD_MS = int(os.environ.get("THRESHOLD_MS") or "2000")  # ms threshold

os.makedirs(LOG_DIR, exist_ok=True)

s3 = boto3.client('s3')
sns = boto3.client('sns')

def check_url(url, timeout=10):
    start = time.time()
    try:
        r = requests.get(url, timeout=timeout)
        elapsed = int((time.time() - start) * 1000)
        return {
            "url": url,
            "status": r.status_code,
            "response_ms": elapsed,
            "ok": 200 <= r.status_code < 300,
            "error": ""
        }
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        return {
            "url": url,
            "status": None,
            "response_ms": elapsed,
            "ok": False,
            "error": str(e)
        }

def append_csv(logfile, rows):
    header = ["timestamp","url","status","response_ms","ok","error"]
    exists = os.path.exists(logfile)
    with open(logfile, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not exists:
            writer.writeheader()
        for r in rows:
            writer.writerow({
                "timestamp": r["timestamp"],
                "url": r["url"],
                "status": r["status"],
                "response_ms": r["response_ms"],
                "ok": r["ok"],
                "error": r["error"]
            })

def upload_to_s3(local_path, bucket, key):
    try:
        s3.upload_file(local_path, bucket, key)
        return True
    except ClientError as e:
        print("S3 upload error:", e)
        return False

def notify_sns(topic_arn, subject, message):
    try:
        sns.publish(TopicArn=topic_arn, Subject=subject, Message=message)
        return True
    except ClientError as e:
        print("SNS publish error:", e)
        return False

def main():
    if not os.path.exists(URLS_FILE):
        print(f"{URLS_FILE} not found. Add URLs one per line.")
        return

    with open(URLS_FILE) as f:
        urls = [line.strip() for line in f if line.strip()]

    results = []
    now = datetime.datetime.utcnow().isoformat() + "Z"
    issues = []

    for u in urls:
        r = check_url(u)
        r["timestamp"] = now
        results.append(r)
        if not r["ok"] or (r["response_ms"] and r["response_ms"] > THRESHOLD_MS):
            issues.append(r)

    # Write log locally
    run_filename = f"monitor_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.csv"
    local_path = os.path.join(LOG_DIR, run_filename)
    append_csv(local_path, results)

    # Upload log to S3
    s3_key = f"{S3_PREFIX}/{run_filename}"
    uploaded = upload_to_s3(local_path, S3_BUCKET, s3_key)
    print("Uploaded to S3:", uploaded, s3_key)

    # Notify via SNS if issues
    if issues:
        lines = [f"{i['url']} status={i['status']} resp_ms={i['response_ms']} err={i['error']}" for i in issues]
        subject = f"[ALERT] {len(issues)} site issue(s) detected"
        message = "Detected issues:\n" + "\n".join(lines) + f"\n\nLog: s3://{S3_BUCKET}/{s3_key}"
        sent = notify_sns(SNS_TOPIC_ARN, subject, message)
        print("SNS sent:", sent)
    else:
        print("All OK.")

if __name__ == "__main__":
    main()
