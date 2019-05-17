from django.contrib.postgres.fields import JSONField
from django.db import models

from db.model_base import ModelBase


class RefreshToken(ModelBase):
    """
    Record of issued refreshed tokens for users.

    This enables the blacklisting of tokens by
    - inserting newer token for a user (only consider most recent token valid)
    - removing token from the table
    """

    user = models.ForeignKey("User", on_delete=models.PROTECT)
    token_id = models.CharField(primary_key=True, max_length=255)
    token_payload = JSONField()
