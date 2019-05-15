import datetime
import decimal
import enum
import json

from .model import data_model
from .serialize import DataModelSerializer


@data_model
class Person:
    name: str
    age: int
    occupation: str = None


class Animal(str, enum.Enum):
    CAT = "CAT"
    DOG = "DOG"
    WHALE = "WHALE"


class Status(int, enum.Enum):
    UNKNOWN = 0
    SUCCESSFUL = 1


def test():
    dtime = datetime.datetime(2014, 1, 1, 4, 20, 0, 0, tzinfo=datetime.timezone.utc)
    data = {
        "person": Person(name="George", age=20),
        "dtime": dtime,
        "date": dtime.date(),
        "time": dtime.time(),
        "string": "test",
        "int": 100,
        "float": 100.0,
        "decimal": decimal.Decimal(1),
        "set": {3, 2, 4},
        "intenum": Status.SUCCESSFUL,
        "strenum": Animal.WHALE,
    }

    expected_json = (
        '{"date": "2014-01-01", '
        '"decimal": 1.0, '
        '"dtime": "2014-01-01T04:20:00+00:00", '
        '"float": 100.0, '
        '"int": 100, '
        '"intenum": 1, '
        '"person": {"age": 20, "name": "George", "occupation": null}, '
        '"set": [2, 3, 4], '
        '"strenum": "WHALE", '
        '"string": "test", '
        '"time": "04:20:00"}'
    )

    assert json.dumps(data, cls=DataModelSerializer, sort_keys=True) == expected_json
