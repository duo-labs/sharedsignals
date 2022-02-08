# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import time
from typing import Dict

from swagger_server.events import (
    Events, SecurityEvent,
    SessionRevoked, TokenClaimsChange, CredentialChange,
    AssuranceLevelChange, DeviceComplianceChange
)

from swagger_server.models import Subject


# TODO: 1. Support RISC
class GenerateEvent:
    def __init__(self):
        self.event_generation_map = {
            "session-revoked": self.session_revoked_event,
            "token-claims-change": self.token_claims_change_event,
            "credential-change": self.credential_change_event,
            "assurance-level-change": self.assurance_level_change_event,
            "device-compliance-change": self.device_compliance_change_event
        }
        self.subject: Subject
        self.event_type: str

    def session_revoked_event(self) -> SecurityEvent:
        session_revoked = SessionRevoked(subject=self.subject)
        return SecurityEvent(
                events=Events(session_revoked=session_revoked)
                )

    def token_claims_change_event(self) -> SecurityEvent:
        token_claims_change = TokenClaimsChange(subject=self.subject)
        return SecurityEvent(
                events=Events(token_claims_change=token_claims_change)
            )

    def credential_change_event(self) -> SecurityEvent:
        credential_change = CredentialChange(subject=self.subject)
        return SecurityEvent(
                events=Events(credential_change=credential_change)
            )

    def assurance_level_change_event(self) -> SecurityEvent:
        assurance_level_change = AssuranceLevelChange(subject=self.subject)
        return SecurityEvent(
                events=Events(assurance_level_change=assurance_level_change)
            )

    def device_compliance_change_event(self) -> SecurityEvent:
        device_compliance_change = DeviceComplianceChange(subject=self.subject)
        return SecurityEvent(
                events=Events(device_compliance_change=
                              device_compliance_change)
            )

    def generate_security_event(self, event_type: str,
                                subject: Subject) -> SecurityEvent:
        if event_type not in self.event_generation_map:
            return None

        self.event_type = event_type
        event_generation_function = self.event_generation_map[event_type]
        self.subject = subject
        return event_generation_function()
