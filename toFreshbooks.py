#!/usr/bin/env python3

import requests
from dotenv import load_dotenv
import json
import logging
import os
import sys
import argparse
import base64
from datetime import datetime
import pytz
from requests.auth import HTTPBasicAuth
from helper import execute_pipeline

load_dotenv()

FRESHBOOK_TIME_ENTRY_URL = os.getenv("FRESHBOOK_TIME_ENTRY_URL")
FRESHBOOK_BEARER_TOKEN = os.getenv("FRESHBOOK_BEARER_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
PROJECT_ID = os.getenv("PROJECT_ID")
SERVICE_ID = os.getenv("SERVICE_ID")
VANCOUVER_TZ_STRING = "America/Vancouver"
VANCOUVER_TZ = pytz.timezone(VANCOUVER_TZ_STRING)
UTC_TZ = pytz.timezone("UTC")
WATSON_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag')
    args = parser.parse_args()
    kwargs = execute_pipeline([
        {"try": decode_json_from_standard_input, "fail": []},
        {"try": loop_through_frames_and_send_to_freshbooks, "fail": []},
    ])


def decode_json_from_standard_input(**kwargs) -> tuple:
    """
    decode watson time entries in json format from standard input
    """
    try:
        kwargs['frames'] = json.load(sys.stdin)
        return True, kwargs
    except Exception as error:
        logging.warning("Unable to decode JSON")
    return False, kwargs


def loop_through_frames_and_send_to_freshbooks(**kwargs) -> tuple:
    frames = kwargs.get('frames')
    for frame in frames:
        payload = build_freshbooks_payload(frame)
        headers = {"Authorization": FRESHBOOK_BEARER_TOKEN}
        response = requests.post(FRESHBOOK_TIME_ENTRY_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(frame['start'] + " - " + frame['project'])
        else:
            print(response.text)
    return True, kwargs


def build_freshbooks_payload(frame: dict) -> dict:
    start = datetime.fromisoformat(frame['start'])
    start_aware = start.replace(tzinfo=UTC_TZ)
    end = datetime.fromisoformat(frame['stop'])
    duration = (end-start).total_seconds()
    return {
        "time_entry": {
            "is_logged": True,
            "duration": int(duration),
            "note": frame['project'],
            "internal": False,
            "retainer_id": None,
            "pending_client": None,
            "pending_project": None,
            "pending_task": None,
            "source": None,
            "started_at": start_aware.isoformat().replace("+00:00", ".000Z"),
            "local_started_at": None,
            "local_timezone": VANCOUVER_TZ_STRING,
            "billable": None,
            "billed": False,
            "identity_id": "10908883",
            "client_id": CLIENT_ID,
            "project_id": PROJECT_ID,
            "service_id": SERVICE_ID}
    }


if __name__ == "__main__":
    main()
