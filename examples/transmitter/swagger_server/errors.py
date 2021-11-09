#!/usr/bin/env python3
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
from typing import Tuple, Dict  

from connexion import ProblemException, AbstractApp
from connexion.exceptions import OAuthProblem
from pydantic.error_wrappers import ValidationError

from swagger_server.models import Subject, Error


class TransmitterError(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__()


class LongPollingNotSupported(TransmitterError):
    def __init__(self) -> None:
        message = (
            'This Transmitter does not support long polling. '
            'Please try again with return_immediately=True.'
        )
        super().__init__(404, message)


class EmailSubjectNotFound(TransmitterError):
    def __init__(self, subject: Subject) -> None:
        message = f'Email not found in subject: {subject.dict()}'
        super().__init__(404, message)


class SubjectNotInStream(TransmitterError):
    def __init__(self, email_address: str) -> None:
        message = (
            f'There is no subject with this email address associated with '
            f'this stream: {email_address}'
        )
        super().__init__(404, message)


class StreamDoesNotExist(TransmitterError):
    def __init__(self) -> None:
        message = (
            'There is no Event Stream associated with that bearer token. '
            'To use this endpoint, first create an Event Stream with a POST to /register, '
            'and use the resulting token for authenticated requests.'
        )
        super().__init__(404, message)


def connexion_error_hanlder(error: ProblemException) -> Tuple[Dict[str, str], int]:
    return { 'code': str(error.status), 'message': error.detail }, error.status


def auth_error_handler(error: OAuthProblem) -> Tuple[Dict[str, str], int]:
    return { 'code': str(error.code), 'message': error.description }, error.code


def pydantic_error_handler(error: ValidationError) -> Tuple[Dict[str, str], int]:
    code = 400
    return { 'code': str(code), 'message': str(error) }, code


def transmitter_error_handler(error: TransmitterError) -> Tuple[Dict[str, str], int]:
    return { 'code': str(error.code), 'message': error.message }, error.code


def generic_error_handler(error: Exception) -> Tuple[Dict[str, str], int]:
    code = 500
    return { 'code': str(code), 'message': str(error) }, code


def register_error_handlers(app: AbstractApp) -> None:
    app.add_error_handler(ProblemException, connexion_error_hanlder)
    app.add_error_handler(OAuthProblem, auth_error_handler)
    app.add_error_handler(ValidationError, pydantic_error_handler)
    app.add_error_handler(TransmitterError, transmitter_error_handler)
    app.add_error_handler(Exception, generic_error_handler)
