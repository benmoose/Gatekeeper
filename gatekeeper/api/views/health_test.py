from django.test import Client
from django.urls import reverse

from .health import health


def test_health_returns_200():
    response = Client().get(reverse(health))
    assert 200 == response.status_code
