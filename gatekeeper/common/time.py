from datetime import datetime

import pytz
from django.conf import settings


def get_current_utc_time() -> datetime:
    """
    Return the system's current time as a timezone-aware datetime, with tzinfo=utc.
    >>> isinstance(get_current_utc_time(), datetime)
    True
    >>> get_current_utc_time().tzinfo
    <UTC>
    """
    if settings.IS_TEST_ENVIRONMENT:
        return settings.TEST_CURRENT_TIME
    return datetime.now(pytz.UTC)


def to_timestamp(dt: datetime) -> int:
    """
    Return POSIX timestamp as an int representing the number of seconds since Epoch.
    >>> to_timestamp(datetime(2020, 1, 1, tzinfo=pytz.UTC))
    1577836800
    >>> to_timestamp(datetime(2020, 1, 1))
    Traceback (most recent call last):
    ...
    ValueError: Cannot generate timestamps from naive datetimes
    """
    if dt.tzinfo is None:
        raise ValueError("Cannot generate timestamps from naive datetimes")
    return int(dt.timestamp())
