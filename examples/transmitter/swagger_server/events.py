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
    __uri__ = "https://schemas.openid.net/secevent/caep/event-type/"


class SessionRevoked(CAEPEvent):
    pass
    # CAEPEvent.__uri__ += "session-revoked"
    # initiating_entity: str
    
class TokenClaimsChange(CAEPEvent):
    claims: Dict[str, str]
    # CAEPEvent.__uri__ += "token-claims-change"

class CredentialChange(CAEPEvent):
    credential_type: str
    change_type: str
    friendly_name: Optional[str]
    x509_issuer: Optional[str]
    x509_serial: Optional[str]
    fido2_aaguid: Optional[str]
    # CAEPEvent.__uri__ +=  ""
        

class AssuranceLevelChange(CAEPEvent):
    current_level: str
    previous_level: str
    change_direction: str
    # CAEPEvent.__uri__ += "assurance-level-change"
    
class DeviceComplianceChange(CAEPEvent):
    current_status: str
    previous_status: str
    # CAEPEvent.__uri__ += "device-compliance-change"


class Events(BaseModel):
    # SSE
    verification: Optional[VerificationEvent] = Field(alias=VerificationEvent.__uri__)

    # CAEP
    CAEP_event: Optional[CAEPEvent] = Field(alias=CAEPEvent.__uri__)
    session_revoked: Optional[SessionRevoked] = Field(alias=CAEPEvent.__uri__+"session-revoked")
    token_claims_change: Optional[TokenClaimsChange] = Field(alias=CAEPEvent.__uri__+"token-claims-change")
    credential_change: Optional[CredentialChange] = Field(alias=CAEPEvent.__uri__+"credential-change")
    assurance_level_change: Optional[AssuranceLevelChange] = Field(alias=CAEPEvent.__uri__+"assurance-level-change")
    device_compliance_change: Optional[DeviceComplianceChange] = Field(alias=CAEPEvent.__uri__+"device-compliance-change")
    

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
    CAEPEvent.__uri__+"session-revoked",
    CAEPEvent.__uri__+"token-claims-change",
    CAEPEvent.__uri__+"credential-change",
    CAEPEvent.__uri__+"assurance-level-change",
    CAEPEvent.__uri__+"device-compliance-change"
]
