# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

from __future__ import annotations
from typing import Dict, List, Union, Any

from swagger_server.business_logic.const import (
    MIN_VERIFICATION_INTERVAL, POLL_ENDPOINT, TRANSMITTER_ISSUER
)
from swagger_server.business_logic.event import SUPPORTED_EVENTS
from swagger_server.errors import StreamDoesNotExist, SubjectNotInStream
import swagger_server.db as db
from swagger_server.models import PollDeliveryMethod, PushDeliveryMethod
from swagger_server.models import StreamConfiguration
from swagger_server.models import Status


DEFAULT_CONFIG = StreamConfiguration(
    iss=TRANSMITTER_ISSUER,
    aud=[],
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


class Stream:
    def __init__(self,
                 client_id: str,
                 aud: Union[str, List[str]],
                 status: Status = Status.enabled) -> None:
        self.client_id = client_id
        self.config = DEFAULT_CONFIG.copy(update={ 'aud': aud })
        self.status = status

        # Map of subject identifier -> status
        self._subjects: Dict[str, Status] = {}
        self.event_queue: List[Dict[str, Any]] = []

        self._save()

    def _save(self) -> None:
        db.STREAMS[self.client_id] = self

    @classmethod
    def load(cls, client_id: str) -> Stream:
        if client_id in db.STREAMS:
            return db.STREAMS[client_id]
        else:
            raise StreamDoesNotExist()

    @classmethod
    def delete(cls, client_id: str) -> None:
        db.STREAMS.pop(client_id, None)

    def update_config(self, new_config: StreamConfiguration) -> Stream:
        config = self.config.dict()
        if isinstance(new_config.delivery, PollDeliveryMethod):
            new_config.delivery.endpoint_url = POLL_ENDPOINT
        _new_config = new_config.dict()

        for key in READ_ONLY_CONFIG_FIELDS:
            _new_config.pop(key, None)
        config.update(_new_config)

        supported = set(config['events_supported'] or [])
        requested = set(config['events_requested'] or [])

        config['events_delivered'] = list(supported.intersection(requested))
        self.config = StreamConfiguration.parse_obj(config)
        return self

    def get_subject_status(self, email_address: str) -> Status:
        if email_address not in self._subjects:
            raise SubjectNotInStream(email_address)

        return self._subjects[email_address]

    def set_subject_status(self, email_address: str, status: Status) -> None:
        if email_address not in self._subjects:
            raise SubjectNotInStream(email_address)

        self._subjects[email_address] = status

    def add_subject(self, email_address: str) -> None:
        if email_address not in self._subjects:
            # When adding a subject, default them to enabled.
            # This isn't required by the SSE spec,
            # but is default behavior we thought made sense.
            self._subjects[email_address] = Status.enabled

    def remove_subject(self, email_address: str) -> None:
        if email_address in self._subjects:
            self._subjects.pop(email_address)

    def queue_event(self, event: Dict[str, Any]) -> None:
        self.event_queue.append(event)


# Add a stream for https://popular-app.com automatically on startup
Stream(
    client_id='49e5e7785e4e4f688aa49e2585970370',
    aud='https://popular-app.com',
)
