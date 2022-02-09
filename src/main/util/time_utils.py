import pytz

from datetime import datetime
from typing_extensions import Literal


def get_now(
        format_str: str = "%Y-%m-%d %H:%M:%S", return_type: Literal['datetime', 'string', 'timestamp'] = "string",
        timezone: pytz.UTC = pytz.utc
):
    date_str = datetime.now(tz=timezone).strftime(format_str)
    if return_type == "string":
        return date_str
    elif return_type == "timestamp":
        return int(datetime.strptime(date_str, format_str).timestamp())
    return datetime.strptime(date_str, format_str)


def get_now_factory():
    return get_now(return_type="datetime")
