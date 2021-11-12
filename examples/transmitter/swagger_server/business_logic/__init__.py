# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import logging
import time
import uuid
from typing import List, Optional, Tuple, Union, Dict, Any

import requests

import swagger_server.db as db
from swagger_server.business_logic.const import (
    TRANSMITTER_ISSUER, VERIFICATION_EVENT_TYPE, POLL_ENDPOINT
)
from swagger_server import jwt_encode
from swagger_server.business_logic.stream import Stream
from swagger_server.errors import EmailSubjectNotFound, LongPollingNotSupported
from swagger_server.models import StreamConfiguration
from swagger_server.models import StreamStatus
from swagger_server.models import Subject
from swagger_server.models import Status
from swagger_server.models import Email
from swagger_server.models import PushDeliveryMethod, PollDeliveryMethod

from swagger_server.models import TransmitterConfiguration  # noqa: E501

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
    Stream.delete(client_id)
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

    # TODO: Make this a real SET per https://www.rfc-editor.org/rfc/rfc8417.html
    security_event: Dict[str, Any] = {
        'jti': uuid.uuid1().hex,
        'iat': int(time.time()),
        'iss': stream.config.iss,
        'aud': stream.config.aud,
        'events': {
            VERIFICATION_EVENT_TYPE: {}
        }
    }

    if state:
        security_event['events'][VERIFICATION_EVENT_TYPE]['state'] = state

    stream.queue_event(security_event)

    if isinstance(stream.config.delivery, PushDeliveryMethod):
        push_events(stream)


def push_events(stream: Stream) -> None:
    if isinstance(stream.config.delivery, PollDeliveryMethod):
        return

    push_url = stream.config.delivery.endpoint_url

    for event in stream.event_queue:
        headers = {
            "Content-Type": "application/secevent+jwt",
            "Accept": "application/json"
        }

        if stream.config.delivery.authorization_header:
            headers['Authorization'] = stream.config.delivery.authorization_header

        try:
            requests.post(
                push_url,
                data=jwt_encode.encode_set(event),
                headers=headers
            )
        except:
            continue
        
    stream.event_queue = []


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
                 client_id: str) -> Tuple[List[Any], bool]:
    stream = Stream.load(client_id)

    if return_immediately is not None and not return_immediately:
        raise LongPollingNotSupported()

    if acks:
        acks_set = set(acks)
        stream.event_queue = [event for event in stream.event_queue if event['jti'] not in acks_set]

    if max_events is None:
        max_events = len(stream.event_queue)

    more_available = len(stream.event_queue) > max_events

    return stream.event_queue[:max_events], more_available


def register(audience: Union[str, List[str]]) -> Dict[str, str]:
    for stream in db.STREAMS.values():
        if stream.config.aud == audience:
            return { 'token': stream.client_id }

    client_id = uuid.uuid4().hex
    Stream(client_id, audience)
    return { 'token': client_id }
