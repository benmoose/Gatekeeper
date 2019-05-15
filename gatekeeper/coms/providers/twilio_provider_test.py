import json
from pathlib import Path
from typing import List

from .twilio_provider import TwilioProvider

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_get_provider():
    twilio_provider = TwilioProvider.get_provider()
    assert isinstance(twilio_provider, TwilioProvider)


def setup_requests_mock(mocker, url: str, fixture_files: List[str]):
    for i, file in enumerate(fixture_files):
        this_url = url if i == 0 else f"{url}?Page={i}"
        mocker.get(this_url, text=read_fixture_file(fixture_files[i]))


def read_fixture_json(filename):
    return json.loads(read_fixture_file(filename))


def read_fixture_file(filename):
    path = FIXTURES_DIR / filename
    with open(path) as f:
        return f.read()
