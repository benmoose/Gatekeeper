from random import choices
from typing import Iterable
from uuid import uuid4


def generate_verification_code(population: Iterable, length: int) -> str:
    """
    >>> import re
    >>> re.match("^[123]{3}$", generate_verification_code("123", 3)) is not None
    True
    """
    if length < 0:
        raise ValueError("length cannot be less than 0")
    return "".join(choices(population, k=length))


def generate_id(prefix: str) -> str:
    """
    Generate a unique ID suitable for use as a DB primary key.
    >>> import re
    >>> re.match("^bear:[0-9a-f]{32}$", generate_id("bear")) is not None
    True
    """
    if prefix in [None, ""]:
        raise ValueError("prefix cannot be empty")
    uuid = str(uuid4()).replace("-", "")
    return f"{prefix}:{uuid}"
