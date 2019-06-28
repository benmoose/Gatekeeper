from django.db import models

from common.generate import generate_id
from db.model_base import ModelBase

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
    is_active = models.BooleanField(default=True)
