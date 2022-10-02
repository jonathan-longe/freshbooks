#!/usr/bin/env python3

import requests
import json
import logging
import sys
from config import Config
from datetime import datetime
from helper import execute_pipeline


def main():
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
        headers = {"Authorization": Config.FRESHBOOK_BEARER_TOKEN}
        response = requests.post(Config.FRESHBOOK_TIME_ENTRY_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(frame['start'] + " - " + frame['project'])
        else:
            print(response.text)
    return True, kwargs


def build_freshbooks_payload(frame: dict) -> dict:
    start = datetime.fromisoformat(frame['start'])
    start_aware = start.replace(tzinfo=Config.UTC_TZ)
    end = datetime.fromisoformat(frame['stop'])
    exact_duration = int((end-start).total_seconds())
    duration = round_duration_to_quarter_hour(exact_duration)
    return {
        "time_entry": {
            "is_logged": True,
            "duration": duration,
            "note": frame['project'],
            "internal": False,
            "retainer_id": None,
            "pending_client": None,
            "pending_project": None,
            "pending_task": None,
            "source": None,
            "started_at": start_aware.isoformat().replace("+00:00", ".000Z"),
            "local_started_at": None,
            "local_timezone": Config.VANCOUVER_TZ_STRING,
            "billable": None,
            "billed": False,
            "identity_id": "10908883",
            "client_id": Config.CLIENT_ID,
            "project_id": Config.PROJECT_ID,
            "service_id": Config.SERVICE_ID}
    }


def round_duration_to_quarter_hour(duration_seconds: int) -> int:
    """
    Time is billed in 15min increments.  Round inputted duration given in seconds to nearest 15min duration.
    :param duration_seconds:
    :return:
    """
    billable_unit_seconds = 15 * 60
    number_billable_units, remainder = divmod(duration_seconds, billable_unit_seconds)
    if remainder < Config.ROUNDING_SECONDS:
        # number of seconds over billable unit is small -- don't bill it
        return number_billable_units * billable_unit_seconds
    else:
        # number of seconds over billable unit exceed threshold - add another block of time
        return (number_billable_units * billable_unit_seconds) + billable_unit_seconds


if __name__ == "__main__":
    main()
