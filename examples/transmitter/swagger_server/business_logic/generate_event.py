import logging
import time
import uuid

from swagger_server.events import (
    Events, SecurityEvent,
    SessionRevoked,TokenClaimsChange, CredentialChange,
    AssuranceLevelChange, DeviceComplianceChange
)

from swagger_server.models import Subject

TIMESTAMP=873645873
ADMIN_MSG = dict(en="Device compliance change")
USER_MSG = dict(en="Device out of compliance: firewall off")

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
        self.subject:Subject

    
    def session_revoked_event(self)->SecurityEvent:
        session_revoked = SessionRevoked( subject=self.subject,
                        event_timestamp=TIMESTAMP,
                        initiating_entity="Duo policy",
                        reason_admin=ADMIN_MSG,
                        reason_user=USER_MSG)
        return SecurityEvent(
        events=Events(session_revoked=session_revoked)
    )
    
    def token_claims_change_event(self)->SecurityEvent:
        token_claims_change = TokenClaimsChange( subject=self.subject,
                        event_timestamp=TIMESTAMP,
                        initiating_entity="Duo policy",
                        reason_admin=ADMIN_MSG,
                        reason_user=USER_MSG,
                        claims={"trusted_network": "false"})
        return SecurityEvent(
        events=Events(token_claims_change=token_claims_change)
    )
        
    def credential_change_event(self)->SecurityEvent:
        credential_change = CredentialChange( subject=self.subject,
                        event_timestamp=TIMESTAMP,
                        initiating_entity="Duo policy",
                        reason_admin=ADMIN_MSG,
                        reason_user=USER_MSG,
                        credential_type="",
                        change_type="")
        return SecurityEvent(
        events=Events(credential_change=credential_change)
    )
        
    def assurance_level_change_event(self)->SecurityEvent:
        assurance_level_change = AssuranceLevelChange( subject=self.subject,
                        event_timestamp=TIMESTAMP,
                        initiating_entity="Duo policy",
                        reason_admin=ADMIN_MSG,
                        reason_user=USER_MSG,
                        current_level="",
                        previous_level="",
                        change_direction="")
        return SecurityEvent(
        events=Events(assurance_level_change=assurance_level_change)
    )
        
    def device_compliance_change_event(self)->SecurityEvent:
        device_compliance_change = DeviceComplianceChange( subject=self.subject,
                        event_timestamp=TIMESTAMP,
                        initiating_entity="Duo policy",
                        reason_admin=ADMIN_MSG,
                        reason_user=USER_MSG,
                        current_status="",
                        previous_status="")
        return SecurityEvent(
        events=Events(device_compliance_change=device_compliance_change)
    )
        
    def generate_security_event(self,event_type:str,subject:Subject)->SecurityEvent:
        if event_type not in self.event_generation_map:
            return None

        event_generation_function = self.event_generation_map[event_type]
        self.subject = subject
        return event_generation_function()