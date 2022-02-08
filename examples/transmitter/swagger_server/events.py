# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
from enum import Enum
import time
from typing import ClassVar, Dict, Optional
import uuid

from pydantic import AnyUrl, BaseModel, Field

from swagger_server.models import Subject

CAEP_BASE_URI = "https://schemas.openid.net/secevent/caep/event-type"


# Enums

class AssuranceLevels(Enum):
    nist_aal1 = 'nist-aal1'
    nist_aal2 = 'nist-aal2'
    nist_aal3 = 'nist-aal3'


class AssuranceDirections(Enum):
    increase = 'increase'
    decrease = 'decrease'


class CredentialChangeTypes(Enum):
    create = 'create'
    revoke = 'revoke'
    update = 'update'
    delete = 'delete'


class CredentialTypes(Enum):
    password = 'password'
    pin = 'pin'
    x509 = 'x509'
    fido2_platform = 'fido2-platform'
    fido2_roaming = 'fido2-roaming'
    fido_u2f = 'fido-u2f'
    verifiable_credential = 'verifiable-credential'
    phone_voice = 'phone-voice'
    phone_sms = 'phone-sms'
    app = 'app'


class DeviceStatuses(Enum):
    compliant = 'compliant'
    not_compliant = 'not-compliant'


# Models

class Event(BaseModel):
    __uri__: ClassVar[AnyUrl]

    class Config:
        underscore_attrs_are_private = True


class VerificationEvent(Event):
    __uri__ = "https://schemas.openid.net/secevent/sse/event-type/verification"
    state: Optional[str]


class CAEPEvent(Event):
    # use this, can't use init
    # https://stackoverflow.com/questions/63616798/
    # pydantic-how-to-pass-the-default-value-to-a-variable-if-none-was-passed
    subject: Subject
    event_timestamp: Optional[int] = Field(
        default_factory=lambda: int(time.time()))
    initiating_entity: Optional[str] = 'Duo policy'
    reason_admin: Optional[Dict[str, str]]
    reason_user: Optional[Dict[str, str]]


class SessionRevoked(CAEPEvent):
    # class variable shared by all instances
    __uri__ = f"{CAEP_BASE_URI}/session-revoked"


class TokenClaimsChange(CAEPEvent):
    # class variable shared by all instances
    __uri__ = f"{CAEP_BASE_URI}/token-claims-change"
    claims: Dict[str, str] = {"trusted_network": "false"}


class CredentialChange(CAEPEvent):
    # class variable shared by all instances
    __uri__ = f"{CAEP_BASE_URI}/credential-change"
    credential_type: CredentialTypes = CredentialTypes.fido2_roaming
    change_type: CredentialChangeTypes = CredentialChangeTypes.create
    friendly_name: Optional[str]
    x509_issuer: Optional[str]
    x509_serial: Optional[str]
    fido2_aaguid: Optional[str]


class AssuranceLevelChange(CAEPEvent):
    # class variable shared by all instances
    __uri__ = f"{CAEP_BASE_URI}/assurance-level-change"
    current_level: AssuranceLevels = AssuranceLevels.nist_aal2
    previous_level: AssuranceLevels = AssuranceLevels.nist_aal1
    change_direction: AssuranceDirections = AssuranceDirections.increase


class DeviceComplianceChange(CAEPEvent):
    # class variable shared by all instances
    __uri__ = f"{CAEP_BASE_URI}/device-compliance-change"
    current_status: DeviceStatuses = DeviceStatuses.compliant
    previous_status: DeviceStatuses = DeviceStatuses.not_compliant


class Events(BaseModel):
    # SSE
    verification: Optional[VerificationEvent] = Field(
        alias=VerificationEvent.__uri__)

    # CAEP
    session_revoked: Optional[SessionRevoked] = Field(
        alias=SessionRevoked.__uri__)
    token_claims_change: Optional[TokenClaimsChange] = Field(
        alias=TokenClaimsChange.__uri__)
    credential_change: Optional[CredentialChange] = Field(
        alias=CredentialChange.__uri__)
    assurance_level_change: Optional[AssuranceLevelChange] = Field(
        alias=AssuranceLevelChange.__uri__)
    device_compliance_change: Optional[DeviceComplianceChange] = Field(
        alias=DeviceComplianceChange.__uri__)

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
    SessionRevoked.__uri__,
    TokenClaimsChange.__uri__,
    CredentialChange.__uri__,
    AssuranceLevelChange.__uri__,
    DeviceComplianceChange.__uri__
]
