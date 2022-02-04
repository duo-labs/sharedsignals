# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import logging
import uuid
from typing import List, Optional, Tuple, Union, Dict

from swagger_server.events import (
    Events, SecurityEvent, VerificationEvent
)
from swagger_server.business_logic.const import TRANSMITTER_ISSUER
from swagger_server.business_logic.stream import Stream
from swagger_server.business_logic.generate_event import GenerateEvent
from swagger_server.errors import (
EmailSubjectNotFound, LongPollingNotSupported, TransmitterError
)
from swagger_server.models import (
   Email, Status, StreamConfiguration, StreamStatus, 
   Subject, TransmitterConfiguration
)
from swagger_server.utils import get_simple_subject

log = logging.getLogger(__name__)


def add_subject(subject: Subject,
                verified: Optional[bool],
                client_id: str) -> None:
    simple_subj = get_simple_subject(subject, Email)
    if not simple_subj:
        raise EmailSubjectNotFound(subject)

    stream = Stream.load(client_id)
    stream.add_subject(simple_subj.email)


def get_status(subject: Optional[Subject], client_id: str) -> StreamStatus:
    stream = Stream.load(client_id)

    if not subject:
        return StreamStatus(
            status=stream.status,
        )

    simple_subj = get_simple_subject(subject, Email)
    if not simple_subj:
        raise EmailSubjectNotFound(subject)

    return StreamStatus(
        status=stream.get_subject_status(simple_subj.email),
        subject=subject,
    )


def remove_subject(subject: Subject, client_id: str) -> None:
    simple_subj = get_simple_subject(subject, Email)
    if not simple_subj:
        raise EmailSubjectNotFound(subject)

    stream = Stream.load(client_id)
    stream.remove_subject(simple_subj.email)


def stream_post(stream_configuration: StreamConfiguration,
                client_id: str) -> StreamConfiguration:
    stream = Stream.load(client_id)

    stream = stream.update_config(stream_configuration)
    return stream.config


def stream_delete(client_id: str) -> None:
    stream = Stream.load(client_id)
    stream.delete()
    return None


def stream_get(client_id: str) -> StreamConfiguration:
    return Stream.load(client_id).config


def update_status(status: Status,
                  subject: Optional[Subject],
                  reason: Optional[str],
                  client_id: str) -> StreamStatus:
    stream = Stream.load(client_id)

    if not subject:
        stream.status = status
        stream.save()
        return StreamStatus(
            status=status,
        )

    simple_subj = get_simple_subject(subject, Email)
    if not simple_subj:
        raise EmailSubjectNotFound(subject)

    stream.set_subject_status(simple_subj.email, status)
    return StreamStatus(
        status=status,
        subject=subject,
    )


def verification_request(state: Optional[str], client_id: str) -> None:
    stream = Stream.load(client_id)

    security_event = SecurityEvent(
        events=Events(verification=VerificationEvent(state=state))
    )
    stream.process_SET(security_event)


def _well_known_sse_configuration_get(url_root: str, 
                                      issuer: Optional[str] = None) -> TransmitterConfiguration:
    return TransmitterConfiguration(
        issuer=TRANSMITTER_ISSUER + (issuer if issuer else ''),
        jwks_uri=url_root + 'jwks.json',
        critical_subject_members=['user'],
        delivery_methods_supported=[
            'https://schemas.openid.net/secevent/risc/delivery-method/push',
            'https://schemas.openid.net/secevent/risc/delivery-method/poll'
        ],
        configuration_endpoint=url_root + 'stream',
        status_endpoint=url_root + 'status',
        add_subject_endpoint=url_root + 'add-subject',
        remove_subject_endpoint=url_root + 'remove-subject',
        verification_endpoint=url_root + 'verification'
    )


def poll_request(max_events: Optional[int],
                 return_immediately: Optional[bool],
                 acks: Optional[List[str]],
                 client_id: str) -> Tuple[List[SecurityEvent], bool]:
    stream = Stream.load(client_id)

    if return_immediately is not None and not return_immediately:
        raise LongPollingNotSupported()

    if acks:
        acks = set(acks)
        stream.ack_SETs(acks)

    queue_length = stream.count_SETs()

    if max_events is None:
        max_events = queue_length

    more_available = queue_length > max_events

    return stream.get_SETs(max_events), more_available


def register(audience: Union[str, List[str]]) -> Dict[str, str]:
    client_id = uuid.uuid4().hex
    Stream(client_id, audience)
    return { 'token': client_id }


def trigger_event(event_type:str,subject: Subject)->None:
    # TODO: 2. allocate a GenerateEvent only once

    ge = GenerateEvent()
    security_event = ge.generate_security_event(event_type,subject)
    if security_event is None:
        raise TransmitterError(code=500,message=f"invalid event_type:{event_type} (only RISC and CAEP supported)")
    # and broadcast it
    Stream.broadcast_SET(security_event)