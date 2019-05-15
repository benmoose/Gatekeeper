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
