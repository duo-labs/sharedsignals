import pydantic

from openid_sse.models.common import URI_REGEX
from openid_sse.models.events.event import Event


class EventMap(pydantic.BaseModel):
    """A base model for the SET 'events' field value for any SSE event"""
    @pydantic.root_validator(pre=True)
    def valid_keys(cls, values):
        """Ensure all keys are URIs"""
        for key in values.keys():
            # key must be a URI
            if not URI_REGEX.match(key):
                raise TypeError("'events' keys must be in URI format")
        return values

    @pydantic.root_validator(pre=False)
    def valid_values(cls, values):
        """Ensure all dictionary values are Events"""
        for value in values.values():
            # value must be an event
            if not isinstance(value, Event):
                raise TypeError("'events' values must be a subtype of Event")
        return values
