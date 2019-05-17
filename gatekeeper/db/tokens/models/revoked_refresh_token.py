from django.db import models

from db.model_base import ModelBase


class RevokedRefreshToken(ModelBase):
    user = models.ForeignKey("User", on_delete=models.PROTECT)
    token_id = models.CharField(max_length=255, unique=True)
    token_issued_at = models.DateTimeField()
    token_expires_at = models.DateTimeField(db_index=True)
