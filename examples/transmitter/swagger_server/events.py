# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
import time
from typing import ClassVar, Dict, Optional
import uuid

from pydantic import AnyUrl, BaseModel, Field

from swagger_server.models import Subject


class Event(BaseModel):
    __uri__: ClassVar[AnyUrl]

    class Config:
        underscore_attrs_are_private = True


class VerificationEvent(Event):
    __uri__ = "https://schemas.openid.net/secevent/sse/event-type/verification"
    state: Optional[str]


class CAEPEvent(Event):
    subject: Subject
    event_timestamp: Optional[int]
    initiating_entity: Optional[str]
    reason_admin: Optional[Dict[str, str]]
    reason_user: Optional[Dict[str, str]]


class SessionRevoked(CAEPEvent):
    __uri__ = "https://schemas.openid.net/secevent/caep/event-type/session-revoked"


class Events(BaseModel):
    # SSE
    verification: Optional[VerificationEvent] = Field(alias=VerificationEvent.__uri__)

    # CAEP
    session_revoked: Optional[SessionRevoked] = Field(alias=SessionRevoked.__uri__)

    class Config:
        allow_population_by_field_name = True


class SecurityEvent(BaseModel):
    jti: str = Field(default_factory=lambda: uuid.uuid1().hex)
    iat: int = Field(default_factory=lambda: int(time.time()))
    iss: Optional[str]
    aud: Optional[str]
    events: Events


SUPPORTED_EVENTS = [
    VerificationEvent.__uri__,
    SessionRevoked.__uri__
]
