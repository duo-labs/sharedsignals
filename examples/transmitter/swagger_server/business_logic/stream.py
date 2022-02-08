# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

from __future__ import annotations
from typing import Dict, List, Union, Any, Optional
import json
import logging

import requests
from requests.exceptions import RequestException

from swagger_server.business_logic.const import (
    MIN_VERIFICATION_INTERVAL, POLL_ENDPOINT, TRANSMITTER_ISSUER
)
from swagger_server.events import (
    SecurityEvent, SUPPORTED_EVENTS
)
import swagger_server.db as db
from swagger_server import jwt_encode
from swagger_server.models import (
    Email, PollDeliveryMethod, PushDeliveryMethod,
    StreamConfiguration, Status, Subject
)
from swagger_server.errors import EmailSubjectNotFound, SubjectNotInStream

from swagger_server.utils import get_simple_subject

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
                 status: Status = Status.enabled,
                 save: bool = True) -> None:
        self.client_id = client_id
        self.config = DEFAULT_CONFIG.copy(update={'aud': aud})
        self.status = status

        if save:
            self.save()

    def save(self) -> None:
        stream_data = dict(
            client_id=self.client_id,
            config=self.config.dict(),
            status=self.status.value
        )
        db.save_stream(self.client_id, json.dumps(stream_data))

    @classmethod
    def load(cls, client_id: str) -> Stream:
        stream_data = db.load_stream(client_id)
        new_stream = cls(
            client_id=stream_data["client_id"],
            aud=stream_data["config"]["aud"],
            status=Status(stream_data["status"]),
            save=False
        )
        new_stream.update_config(
            StreamConfiguration(**stream_data["config"]),
            save=False
        )
        return new_stream

    def delete(self) -> None:
        """
        Wipe out any subjects or SETs and
        revert the config to the default
        """
        db.delete_SETs(self.client_id)
        db.delete_subjects(self.client_id)

        # revert the stream to the default config
        audience = self.config.aud
        self.config = DEFAULT_CONFIG.copy(
            update={'aud': audience}
        )
        self.save()

    def update_config(self, new_config: StreamConfiguration,
                      save: bool = True) -> Stream:
        config = self.config.dict()
        _new_config = new_config.dict()

        for key in READ_ONLY_CONFIG_FIELDS:
            _new_config.pop(key, None)
        config.update(_new_config)

        supported = set(config['events_supported'] or [])
        requested = set(config['events_requested'] or [])

        config['events_delivered'] = list(supported.intersection(requested))
        self.config = StreamConfiguration.parse_obj(config)
        if save:
            self.save()
        return self

    def get_subject_status(self, email_address: str) -> Status:
        return db.get_subject_status(self.client_id, email_address)

    def set_subject_status(self, email_address: str, status: Status) -> None:
        db.set_subject_status(self.client_id, email_address, status)

    def add_subject(self, email_address: str) -> None:
        db.add_subject(self.client_id, email_address)

    def remove_subject(self, email_address: str) -> None:
        db.remove_subject(self.client_id, email_address)

    def process_SET(self, SET: SecurityEvent) -> None:
        """Either push the SET or add it to the queue"""
        # make sure the SET is appropriate for this stream
        SET = SET.copy(deep=True)
        SET.iss = self.config.iss
        SET.aud = self.config.aud

        # push or add to queue
        if isinstance(self.config.delivery, PushDeliveryMethod):
            self.push(SET)
        else:
            self.queue_SET(SET)

    def push(self, SET: SecurityEvent, save_on_error=True) -> bool:
        """Push a SET to the push endpoint. If error pushing and save_on_error
        is True, send SET to queue to be pushed by scheduled job
        """

        headers = {
            "Content-Type": "application/secevent+jwt",
            "Accept": "application/json"
        }

        if self.config.delivery.authorization_header:
            headers["Authorization"] = \
                self.config.delivery.authorization_header

        try:
            response = requests.post(
                self.config.delivery.endpoint_url,
                data=jwt_encode.encode_set(SET),
                headers=headers
            )

            response.raise_for_status()
            return True
        except RequestException as err:
            logging.error(
                f"Error pushing SET {SET.jti} to "
                f"{self.config.delivery.endpoint_url}: {err}."
                f"Queuing SET to be picked up by scheduled job instead."
            )
            if save_on_error:
                self.queue_SET(SET)

            return False

    def queue_SET(self, SET: SecurityEvent) -> None:
        db.add_set(self.client_id, SET)

    def get_SETs(self,
                 max_events: Optional[int] = None) -> List[SecurityEvent]:
        return db.get_SETs(self.client_id, max_events)

    def count_SETs(self) -> int:
        return db.count_SETs(self.client_id)

    def ack_SETs(self, jtis: List[str]) -> None:
        db.delete_SETs(self.client_id, jtis)

    @staticmethod
    def broadcast_SET(SET: SecurityEvent) -> None:
        """Send an event to every stream"""
        # these cannot be verification events
        if SET.events.verification is not None:
            raise ValueError("Cannot broadcast Verification Events")

        # assume this is a session revoked SET (the only other one we support)
        # TODO: change this to support all CAEP and RISC
        if SET.events.session_revoked:
            subject = SET.events.session_revoked.subject
        elif SET.events.token_claims_change:
            subject = SET.events.token_claims_change.subject
        elif SET.events.credential_change:
            subject = SET.events.credential_change.subject
        elif SET.events.assurance_level_change:
            subject = SET.events.assurance_level_change.subject
        elif SET.events.device_compliance_change:
            subject = SET.events.device_compliance_change.subject
        else:
            # handle error
            subject = Subject()

        simple_subj = get_simple_subject(subject, Email)
        if not simple_subj:
            raise EmailSubjectNotFound(subject)

        # broadcast to each stream
        for client_id in db.get_stream_ids():
            _stream = Stream.load(client_id)

            # only transmit if the stream and subject are both enabled
            if _stream.status != Status.enabled:
                continue

            try:
                subject_status = _stream.get_subject_status(simple_subj.email)
            except SubjectNotInStream:
                subject_status = Status.disabled

            if subject_status != Status.enabled:
                continue

            _stream.process_SET(SET)
