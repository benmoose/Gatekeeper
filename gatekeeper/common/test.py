from datetime import datetime
from unittest import mock

from .time import get_current_utc_time


def mock_current_time(testing_module, mock_time: datetime):
    function_path = ".".join([testing_module.__name__, get_current_utc_time.__name__])
    return mock.patch(function_path, return_value=mock_time)
