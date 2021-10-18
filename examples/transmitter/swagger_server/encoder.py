from connexion.apps.flask_app import FlaskJSONEncoder
from enum import Enum
from pydantic import BaseModel


class JSONEncoder(FlaskJSONEncoder):
    include_nulls = False

    def default(self, o):
        if isinstance(o, BaseModel):
            return o.dict(exclude_none=True)
        if isinstance(o, Enum):
            return o.value
        return FlaskJSONEncoder.default(self, o)
