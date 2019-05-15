import enum
import json
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import PurePath

import attr


class DataModelSerializer(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__data_object__"):
            return obj.to_dict()
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, set):
            return sorted(obj)
        if isinstance(obj, PurePath):
            return str(obj)
        if isinstance(obj, enum.Enum):
            return obj.value
        if attr.has(obj):
            return attr.asdict(obj)
        return json.JSONEncoder.default(self, obj)
