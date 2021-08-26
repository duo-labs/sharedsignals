"""Defines the SET model described by RFC 8417:
https://datatracker.ietf.org/doc/html/rfc8417
"""
from typing import Optional, Text

from openid_sse.models.jwt import JWT
from openid_sse.models.events.event_map import EventMap


class SET(JWT):
    """https://datatracker.ietf.org/doc/html/rfc8417#section-2
    This specification defines the Security Event Token (SET) data
    structure.  A SET describes statements of fact from the perspective
    of an issuer about a subject.  These statements of fact represent an
    event that occurred directly to or about a security subject, for
    example, a statement about the issuance or revocation of a token on
    behalf of a subject.  This specification is intended to enable
    representing security- and identity-related events.  A SET is a JSON
    Web Token (JWT), which can be optionally signed and/or encrypted.
    SETs can be distributed via protocols such as HTTP.

    The SET defined in this package is further restricted to the definitons
    provided in SSE's standards:

    1. https://openid.net/specs/openid-sse-framework-1_0-01.html#rfc.section.4
    The keys in the events dictionary MUST be URIs

    2.
    """
    # https://datatracker.ietf.org/doc/html/rfc8417#section-2.2
    # "events" (Security Events) Claim
    # This claim contains a set of event statements that each provide
    # information describing a single logical event that has occurred
    # about a security subject (e.g., a state change to the subject).
    # Multiple event identifiers with the same value MUST NOT be used.
    # The "events" claim MUST NOT be used to express multiple
    # independent logical events.

    # The value of the "events" claim is a JSON object whose members are
    # name/value pairs whose names are URIs identifying the event
    # statements being expressed.  Event identifiers SHOULD be stable
    # values (e.g., a permanent URL for an event specification).  For
    # each name present, the corresponding value MUST be a JSON object.
    # The JSON object MAY be an empty object ("{}"), or it MAY be a JSON
    # object containing data described by the profiling specification.
    events: EventMap

    # https://datatracker.ietf.org/doc/html/rfc8417#section-2.2
    # "txn" (Transaction Identifier) Claim
    # An OPTIONAL string value that represents a unique transaction
    # identifier.  In cases in which multiple related JWTs are issued,
    # the transaction identifier claim can be used to correlate these
    # related JWTs.  Note that this claim can be used in JWTs that are
    # SETs and also in JWTs using non-SET profiles.
    txn: Optional[Text]

    # https://datatracker.ietf.org/doc/html/rfc8417#section-2.2
    # "toe" (Time of Event) Claim
    # A value that represents the date and time at which the event
    # occurred.  This value is a NumericDate (see Section 2 of
    # [RFC7519]).  By omitting this claim, the issuer indicates that
    # they are not sharing an event time with the recipient.  (Note that
    # in some use cases, the represented time might be approximate;
    # statements about the accuracy of this field MAY be made by
    # profiling specifications.)  This claim is OPTIONAL.
    toe: Optional[int]
