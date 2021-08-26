"""
Defines an Event as described in the SSE spec
https://openid.net/specs/openid-sse-framework-1_0-01.html#rfc.section.4
"""
from typing import ClassVar, Literal, Optional

import pydantic

from openid_sse.models.common import Message, URI
from openid_sse.models.subject import ANY_SUBJECT


class Event(pydantic.BaseModel):
    """https://openid.net/specs/openid-sse-framework-1_0-01.html#rfc.section.4
    The base model for all of the SSE event types. It defines a single
    class variable that must be instantiated, which is the URI of the event.

    It also defines several optional values, which are part of the CAEP
    standard. Because CAEP events are based off of SSE events, and the values
    are optional, it makes sense to define them here:
        - event_timestamp
        - initiating_entity
        - reason_admin
        - reason_user
    """
    __uri__: ClassVar[URI]

    # https://openid.net/specs/openid-sse-framework-1_0-01.html#rfc.section.11.1.2  # noqa: E501
    # The subject of a SSE event is identified by the subject claim within the
    # event payload, whose value is a Subject Identifier. The subject claim is
    # REQUIRED for all SSE events. The JWT sub claim MUST NOT be present in any
    # SET containing a SSE event.
    subject: ANY_SUBJECT

    # https://openid.net/specs/openid-caep-specification-1_0-02.html#rfc.section.2  # noqa: E501
    # the time at which the event described by this SET occurred.
    # Its value is a JSON number representing the number of seconds from
    # 1970-01-01T0:0:0Z as measured in UTC until the date/time.
    event_timestamp: Optional[int]

    # https://openid.net/specs/openid-caep-specification-1_0-02.html#rfc.section.2  # noqa: E501
    # describes the entity that invoked the event
    initiating_entity: Optional[Literal[
        "admin",  # an administrative action triggered the event
        "user",  # an end-user action triggered the event
        "policy",  # a policy evaluation triggered the event
        "system",  # a system or platform assertion triggered the event
    ]]

    # https://openid.net/specs/openid-caep-specification-1_0-02.html#rfc.section.2  # noqa: E501
    # a localizable administrative message intended for logging and auditing.
    # The object MUST contain one or more key/value pairs,
    # with a BCP47 [RFC5646] language tag as the key and the locale-specific
    # administrative message as the value.
    reason_admin: Optional[Message]

    # https://openid.net/specs/openid-caep-specification-1_0-02.html#rfc.section.2  # noqa: E501
    # a localizable user-friendly message for display to an end-user.
    # The object MUST contain one or more key/value pairs,
    # with a BCP47 [RFC5646] language tag as the key and the locale-specific
    # end-user message as the value.
    reason_user: Optional[Message]
