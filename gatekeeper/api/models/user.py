from datetime import datetime

import pytest

from common.model import data_model
from db.user import create_user


@data_model
class User:
    user_id: str
    phone_number: str
    created_on: datetime
    modified_on: datetime

    @classmethod
    def from_db_model(cls, db_model):
        return cls(
            user_id=db_model.user_id,
            phone_number=db_model.phone_number,
            created_on=db_model.created_on,
            modified_on=db_model.modified_on,
        )


@pytest.mark.django_db
def test_user_model():
    db_user = create_user("+447000000000")
    user = User.from_db_model(db_user)

    assert db_user.user_id == user.user_id
    assert "+447000000000" == user.phone_number
