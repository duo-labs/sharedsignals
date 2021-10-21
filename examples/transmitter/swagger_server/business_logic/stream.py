from typing import List, Mapping, Union
import queue

from swagger_server.business_logic.const import (
    MIN_VERIFICATION_INTERVAL, POLL_ENDPOINT, TRANSMITTER_ISSUER
)
from swagger_server.business_logic.event import SUPPORTED_EVENTS
import swagger_server.db as db
from swagger_server.models import PollDeliveryMethod, PushDeliveryMethod
from swagger_server.models import StreamConfiguration
from swagger_server.models import Status


DEFAULT_CONFIG = StreamConfiguration(
    iss=TRANSMITTER_ISSUER,
    aud='',
    events_supported=SUPPORTED_EVENTS,
    events_requested=[],
    events_delivered=[],
    min_verification_interval=MIN_VERIFICATION_INTERVAL,
    delivery=PollDeliveryMethod(endpoint_url=POLL_ENDPOINT)
)

READ_ONLY_CONFIG_FIELDS = {
    'iss',
    'aud',
    'events_supported',
    'events_delivered',
    'min_verification_interval'
}


class SubjectNotInStream(KeyError):
    def __init__(self, email_address):
        self.message = (
            f'There is no subject with this email address associated with '
            f'this stream: {email_address}'
        )
        super().__init__(self.message)


class StreamDoesNotExist(KeyError):
    def __init__(self):
        self.message = (
            f'There is no Event Stream associated with that bearer token. '
            f'To use this endpoint, first create an Event Stream with a POST to /register, '
            f'and use the resulting token for authenticated requests.'
        )
        super().__init__(self.message)


# TODO-T136006 remove this when push_queue gets removed...
class EventQueue:
    def __init__(self):
        self.event_map = {}
        self.event_queue = []

    def put(self, event):
        self.event_map[event.get('jti')] = event
        self.event_queue.append(event)

    def get(self, max_events=1):
        return self.event_queue[-max_events:]

    def delete(self, jti):
        event = self.event_map.get(jti, None)
        if event:
            del self.event_map[jti]
            self.event_queue.remove(event)

    def qsize(self):
        return len(self.event_queue)


class Stream:
    def __init__(self,
                 client_id: str,
                 aud: Union[str, List[str]],
                 status: Status = Status.enabled):
        self.client_id = client_id
        self.config = DEFAULT_CONFIG
        self.config.aud = aud
        self.status = status

        # Map of subject identifier -> status
        self._subjects: Mapping[str, Status] = {}
        self.push_queue = EventQueue()
        self.poll_queue = []

        self._save()

    def _save(self):
        db.STREAMS[self.client_id] = self

    @classmethod
    def load(cls, client_id: str):
        if client_id in db.STREAMS:
            return db.STREAMS[client_id]
        else:
            raise StreamDoesNotExist()

    @classmethod
    def delete(cls, client_id):
        db.STREAMS.pop(client_id, None)

    def update_config(self, new_config: StreamConfiguration):
        config = self.config.dict()
        _new_config = new_config.dict()
        for key in READ_ONLY_CONFIG_FIELDS:
            _new_config.pop(key, None)
        config.update(_new_config)

        supported = set(config['events_supported'] or [])
        requested = set(config['events_requested'] or [])

        config['events_delivered'] = list(supported.intersection(requested))
        self.config = StreamConfiguration.parse_obj(config)
        return self

    def get_subject_status(self, email_address):
        if email_address not in self._subjects:
            raise SubjectNotInStream(email_address)

        return self._subjects[email_address]

    def set_subject_status(self, email_address, status):
        if email_address not in self._subjects:
            raise SubjectNotInStream(email_address)

        self._subjects[email_address] = status

    def add_subject(self, email_address):
        if email_address not in self._subjects:
            # When adding a subject, default them to enabled.
            # This isn't required by the SSE spec,
            # but is default behavior we thought made sense.
            self._subjects[email_address] = Status.enabled

    def remove_subject(self, email_address):
        if email_address in self._subjects:
            self._subjects.pop(email_address)

    def queue_event(self, event):
        if isinstance(self.config.delivery, PushDeliveryMethod):
            self.push_queue.put(event)
        else:  # PollDeliveryMethod
            self.poll_queue.append(event)


# Add a stream for https://popular-app.com automatically on startup
Stream(
    client_id='49e5e7785e4e4f688aa49e2585970370',
    aud='https://popular-app.com',
)
