"""Defines the 'session revoked' signal as described in the CAEP spec
https://openid.net/specs/openid-caep-specification-1_0-02.html
"""
import pydantic

from openid_sse.models.common import URI
from openid_sse.models.set import SET
from openid_sse.models.events.event import Event
from openid_sse.models.events.event_map import EventMap


class SessionRevokedEvent(Event):
    """https://openid.net/specs/openid-caep-specification-1_0-02.html#rfc.section.3.1  # noqa: E501
    Session Revoked signals that the session identified by the subject has been
    revoked. The explicit session identifier may be directly referenced in the
    subject or other properties of the session may be included to allow the
    receiver to identify applicable sessions.
    """
    __uri__ = URI(
        "https://schemas.openid.net/secevent/caep/event-type/session-revoked"
    )


class SessionRevokedEventMap(EventMap):
    """This model defines what the 'events' field should look like in a SET
    that has a SessionRevoked event
    """
    uri: SessionRevokedEvent = pydantic.Field(
        ...,  # this field is required
        alias=str(SessionRevokedEvent.__uri__)
    )


class SessionRevoked(SET):
    """This model is the actual SET to use when you want to broadcast a
    SessionRevoked event
    """
    events: SessionRevokedEventMap
