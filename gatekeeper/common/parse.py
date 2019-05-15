import json
from typing import AnyStr, Optional


def safe_parse_json(json_string: AnyStr) -> Optional[dict]:
    """
    >>> safe_parse_json('{"foo": "bar"}')
    {'foo': 'bar'}
    >>> safe_parse_json(b'{"foo": "bar"}')
    {'foo': 'bar'}
    >>> safe_parse_json("{}")
    {}
    >>> safe_parse_json("nsabfb")
    >>> safe_parse_json("")
    >>> safe_parse_json(None)
    """
    try:
        return json.loads(json_string)
    except Exception:
        return None
