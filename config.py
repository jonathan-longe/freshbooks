import os
import pytz


class Config:
    # Default values are used for testing
    FRESHBOOK_TIME_ENTRY_URL = os.getenv("FRESHBOOK_TIME_ENTRY_URL", "http://localhost/add_time")
    FRESHBOOK_BEARER_TOKEN = os.getenv("FRESHBOOK_BEARER_TOKEN", "Bearer AAABBB")
    CLIENT_ID = os.getenv("CLIENT_ID", "1111")
    PROJECT_ID = os.getenv("PROJECT_ID", "2222")
    SERVICE_ID = os.getenv("SERVICE_ID", "3333")
    VANCOUVER_TZ_STRING = "America/Vancouver"
    VANCOUVER_TZ = pytz.timezone(VANCOUVER_TZ_STRING)
    UTC_TZ = pytz.timezone("UTC")
    WATSON_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

    # Time is billed in quarter hour blocks.
    # Number of seconds beyond a quarter hour that triggers new billable unit
    ROUNDING_SECONDS = 300  # 5 minutes

