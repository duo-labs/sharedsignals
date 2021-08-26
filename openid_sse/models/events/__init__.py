from typing import List, Type

from openid_sse.models.events.caep.session_revoked import SessionRevokedEvent
from openid_sse.models.events.event import Event

EVENT_TYPES: List[Type[Event]] = [
    SessionRevokedEvent,
]

EVENT_MAP = {e.__uri__: e for e in EVENT_TYPES}
