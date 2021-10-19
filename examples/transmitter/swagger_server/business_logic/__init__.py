import logging
import time
import uuid
from typing import List, Mapping, Optional, Tuple

from swagger_server.business_logic.const import (
    TRANSMITTER_ISSUER, VERIFICATION_EVENT_TYPE
)
from swagger_server.business_logic.stream import Stream, StreamDoesNotExist
from swagger_server.models import StreamConfiguration
from swagger_server.models import StreamStatus
from swagger_server.models import Subject
from swagger_server.models import Status
from swagger_server.models import Email

from swagger_server.models import TransmitterConfiguration  # noqa: E501

from swagger_server.utils import get_simple_subject

log = logging.getLogger(__name__)


class LongPollingNotSupported(Exception):
    def __init__(self):
        self.message = (
            'This Transmitter does not support long polling. '
            'Please try again with return_immediately=True.'
        )


class EmailSubjectNotFound(Exception):
    def __init__(self, subject: Subject) -> None:
        self.message = 'Email not found in subject: {}'.format(subject.dict())
        super().__init__(self.message)


def add_subject(subject: Subject,
                verified: Optional[bool],
                client_id: str) -> None:
    simple_subj = get_simple_subject(subject, Email)
    if not simple_subj:
        raise EmailSubjectNotFound(subject)

    stream = Stream.load(client_id)
    stream.add_subject(simple_subj.email)


def get_status(subject: Subject, client_id: str) -> StreamStatus:
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


def stream_post(url_root,
                stream_configuration: StreamConfiguration,
                client_id: str) -> StreamConfiguration:
    try:
        stream = Stream.load(client_id)
    except StreamDoesNotExist:
        stream = Stream(client_id)

    if (stream_configuration.delivery
            and stream_configuration.delivery.method == 'https://schemas.openid.net/secevent/risc/delivery-method/poll'):
        stream_configuration.delivery.endpoint_url = url_root + "poll"

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
    security_event = {
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


def _well_known_sse_configuration_get(url_root, issuer: Optional[str] = None) -> TransmitterConfiguration:
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


def poll_request(max_events: int,
                 return_immediately: bool,
                 acks: List[str],
                 client_id: str) -> Tuple[List[object], bool]:
    stream = Stream.load(client_id)

    if not return_immediately:
        raise LongPollingNotSupported()

    if acks:
        acks = set(acks)
        stream.poll_queue = [event for event in stream.poll_queue if event['jti'] not in acks]

    more_available = len(stream.poll_queue) > max_events

    return stream.poll_queue[:max_events], more_available
