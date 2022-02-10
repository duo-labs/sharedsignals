# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

from swagger_server.events import (
    SecurityEvent,
    SessionRevoked, TokenClaimsChange, CredentialChange,
    AssuranceLevelChange, DeviceComplianceChange
)
from swagger_server.models import (
   Subject, EventType
)


# TODO: 1. Support RISC
event_type_map = {
    EventType.session_revoked: SessionRevoked,
    EventType.token_claims_change: TokenClaimsChange,
    EventType.credential_change: CredentialChange,
    EventType.assurance_level_change: AssuranceLevelChange,
    EventType.device_compliance_change: DeviceComplianceChange
}


def generate_security_event(event_type: EventType,
                            subject: Subject) -> SecurityEvent:
    event_class = event_type_map[event_type]
    event_attribute_name = event_type.value.replace("-", "_")
    security_event = {
        "events": {
            event_attribute_name: event_class(subject=subject),
        }
    }
    return SecurityEvent.parse_obj(security_event)
