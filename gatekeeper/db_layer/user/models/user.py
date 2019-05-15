from django.db import models

from common.generate import generate_id
from db_layer.model_base import ModelBase

USER_ID_PREFIX = "gatekeeper"


def generate_user_id():
    """
    >>> import re
    >>> re.match("^gatekeeper:[0-9a-f]+$", generate_user_id()) is not None
    True
    """
    return generate_id(USER_ID_PREFIX)


class User(ModelBase):
    user_id = models.CharField(
        primary_key=True, max_length=128, default=generate_user_id
    )
    phone_number = models.CharField(max_length=32, unique=True)

    full_name = models.TextField(blank=True)
    short_name = models.TextField(blank=True)
    picture = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
