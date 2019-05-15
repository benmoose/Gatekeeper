import logging

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class ModelBase(models.Model):
    class Meta:
        abstract = True

    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_on = models.DateTimeField(auto_now=True, db_index=True)

    def save_with_times(self, created_on=None, modified_on=None):
        # this should only be used in tests to mock timestamps
        if not settings.IS_TEST_ENVIRONMENT:
            logger.warning(
                "Dangerously calling save_with_times out of test environment"
            )

        if created_on is not None:
            self.created_on = created_on
        if modified_on is not None:
            self.modified_on = modified_on
        super().save()
