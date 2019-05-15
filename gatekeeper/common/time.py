from datetime import datetime

import pytz


def get_current_utc_time() -> datetime:
    """
    Return the system's current time as a timezone-aware datetime, with tzinfo=utc.
    >>> isinstance(get_current_utc_time(), datetime)
    True
    >>> get_current_utc_time().tzinfo
    <UTC>
    """
    return datetime.now(pytz.UTC)
