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
RISC_BASE_URI = "https://schemas.openid.net/secevent/risc/event-type"

# Enums


class AssuranceLevel(Enum):
    nist_aal1 = 'nist-aal1'
    nist_aal2 = 'nist-aal2'
    nist_aal3 = 'nist-aal3'


class AssuranceDirection(Enum):
    increase = 'increase'
    decrease = 'decrease'


class CredentialChangeType(Enum):
    create = 'create'
    revoke = 'revoke'
    update = 'update'
    delete = 'delete'


class CredentialType(Enum):
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


class DeviceStatus(Enum):
    compliant = 'compliant'
    not_compliant = 'not-compliant'


class AccountDisabledReason(Enum):
    hijacking = 'hijacking'
    bulk_account = 'bulk-account'


# Models

class Event(BaseModel):
    __uri__: ClassVar[AnyUrl]

    class Config:
        underscore_attrs_are_private = True


class VerificationEvent(Event):
    __uri__ = "https://schemas.openid.net/secevent/sse/event-type/verification"
    state: Optional[str]


class RISCEvent(Event):
    subject: Subject


class AccountCredentialChangeRequired(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/account-credential-change-required"


class AccountPurged(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/account-purged"


class AccountDisabled(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/account-disabled"
    # optional and enum
    reason: Optional[AccountDisabledReason] = AccountDisabledReason.hijacking


class AccountEnabled(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/account-enabled"


class IdentifierChanged(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/identifier-changed"
    new_value: Optional[str]  # optional and string?


class IdentifierRecycled(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/identifier-recycled"


class CredentialCompromise(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/credential-compromise"
    credential_type: CredentialType = CredentialType.fido2_roaming
    event_timestamp: Optional[int] = Field(
        default_factory=lambda: int(time.time()))
    reason_admin: Optional[Dict[str, str]]
    reason_user: Optional[Dict[str, str]]


class OptIn(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/opt-in"


class OptOutInitiated(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/opt-out-initiated"


class OptOutCancelled(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/opt-out-cancelled"


class OptOutEffective(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/opt-out-effective"


class RecoveryActivated(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/recovery-activated"


class RecoveryInformationChanged(RISCEvent):
    __uri__ = f"{RISC_BASE_URI}/recovery-information-changed"


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
    credential_type: CredentialType = CredentialType.fido2_roaming
    change_type: CredentialChangeType = CredentialChangeType.create
    friendly_name: Optional[str]
    x509_issuer: Optional[str]
    x509_serial: Optional[str]
    fido2_aaguid: Optional[str]


class AssuranceLevelChange(CAEPEvent):
    # class variable shared by all instances
    __uri__ = f"{CAEP_BASE_URI}/assurance-level-change"
    current_level: AssuranceLevel = AssuranceLevel.nist_aal2
    previous_level: AssuranceLevel = AssuranceLevel.nist_aal1
    change_direction: AssuranceDirection = AssuranceDirection.increase


class DeviceComplianceChange(CAEPEvent):
    # class variable shared by all instances
    __uri__ = f"{CAEP_BASE_URI}/device-compliance-change"
    current_status: DeviceStatus = DeviceStatus.compliant
    previous_status: DeviceStatus = DeviceStatus.not_compliant


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

    # RISC
    account_credential_change_required: Optional[AccountCredentialChangeRequired] = Field(
        alias=AccountCredentialChangeRequired.__uri__)
    account_purged: Optional[AccountPurged] = Field(
        alias=AccountPurged.__uri__)
    account_disabled: Optional[AccountDisabled] = Field(
        alias=AccountDisabled.__uri__)
    account_enabled: Optional[AccountEnabled] = Field(
        alias=AccountEnabled.__uri__)
    identifier_changed: Optional[IdentifierChanged] = Field(
        alias=IdentifierChanged.__uri__)
    identifier_recycled: Optional[IdentifierRecycled] = Field(
        alias=IdentifierRecycled.__uri__)
    credential_compromise: Optional[CredentialCompromise] = Field(
        alias=CredentialCompromise.__uri__)
    opt_in: Optional[OptIn] = Field(
        alias=OptIn.__uri__)
    opt_out_initiated: Optional[OptOutInitiated] = Field(
        alias=OptOutInitiated.__uri__)
    opt_out_cancelled: Optional[OptOutCancelled] = Field(
        alias=OptOutCancelled.__uri__)
    opt_out_effective: Optional[OptOutEffective] = Field(
        alias=OptOutEffective.__uri__)
    recovery_activated: Optional[RecoveryActivated] = Field(
        alias=RecoveryActivated.__uri__)
    recovery_information_changed: Optional[RecoveryInformationChanged] = Field(
        alias=RecoveryInformationChanged.__uri__)

    def get_subject(self) -> Subject:
        """
        Retrieves the subject from
        the first non-null event in this events object
        """
        list_of_events = list(self.dict(exclude_none=True).values())
        if not list_of_events:
            raise ValueError("No events in the Events object")

        first_subject = list_of_events[0]["subject"]
        return Subject.parse_obj(first_subject)

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
    DeviceComplianceChange.__uri__,
    AccountCredentialChangeRequired.__uri__,
    AccountPurged.__uri__,
    AccountDisabled.__uri__,
    AccountEnabled.__uri__,
    IdentifierChanged.__uri__,
    IdentifierRecycled.__uri__,
    CredentialCompromise.__uri__,
    OptIn.__uri__,
    OptOutInitiated.__uri__,
    OptOutCancelled.__uri__,
    OptOutEffective.__uri__,
    RecoveryActivated.__uri__,
    RecoveryInformationChanged.__uri__,
]
