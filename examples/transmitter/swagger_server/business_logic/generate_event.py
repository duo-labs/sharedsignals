# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.


from swagger_server.events import (
    SecurityEvent,
    SessionRevoked, TokenClaimsChange, CredentialChange,
    AssuranceLevelChange, DeviceComplianceChange,
    AccountDisabled, AccountEnabled, AccountPurged, IdentifierChanged,
    IdentifierRecycled, CredentialCompromise, OptIn, OptOutCancelled,
    OptOutEffective, OptOutInitiated, RecoveryActivated,
    RecoveryInformationChanged
)
from swagger_server.models import (
   Subject, EventType
)


event_type_map = {
    EventType.session_revoked: SessionRevoked,
    EventType.token_claims_change: TokenClaimsChange,
    EventType.credential_change: CredentialChange,
    EventType.assurance_level_change: AssuranceLevelChange,
    EventType.device_compliance_change: DeviceComplianceChange,
    EventType.account_purged: AccountPurged,
    EventType.account_disabled: AccountDisabled,
    EventType.account_enabled: AccountEnabled,
    EventType.identifier_changed: IdentifierChanged,
    EventType.identifier_recycled: IdentifierRecycled,
    EventType.credential_compromise: CredentialCompromise,
    EventType.opt_in: OptIn,
    EventType.opt_out_initiated: OptOutInitiated,
    EventType.opt_out_cancelled: OptOutCancelled,
    EventType.opt_out_effective: OptOutEffective,
    EventType.recovery_activated: RecoveryActivated,
    EventType.recovery_information_changed: RecoveryInformationChanged,
}


def generate_security_event(event_type: EventType,
                            subject: Subject) -> SecurityEvent:
    event_class = event_type_map[event_type]
    event_attribute_name = event_type.name
    security_event = {
        "events": {
            event_attribute_name: event_class(subject=subject),
        }
    }
    return SecurityEvent.parse_obj(security_event)
