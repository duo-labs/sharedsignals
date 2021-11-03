# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import logging
import os
from pathlib import Path
from typing import Iterator
import uuid

import connexion
from flask.testing import FlaskClient
from flask import Flask
import pytest
from _pytest.monkeypatch import MonkeyPatch

from swagger_server.business_logic.stream import Stream
from swagger_server.encoder import JSONEncoder
from swagger_server.errors import register_error_handlers
from swagger_server import jwt_encode


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    app = create_app({ 'TESTING': True })

    with app.test_client() as client:
        yield client


@pytest.fixture
def new_stream() -> Iterator[Stream]:
    client_id = uuid.uuid4().hex
    stream = Stream(client_id, "https://test-case.popular-app.com")
    yield stream
    Stream.delete(client_id)


def create_app(self) -> Flask:
    logging.getLogger('connexion.operation').setLevel('ERROR')
    app = connexion.App(__name__, specification_dir='../swagger/')
    app.app.json_encoder = JSONEncoder
    app.add_api('swagger.yaml')
    register_error_handlers(app)
    return app.app


@pytest.fixture(autouse=True)
def jwks_path(monkeypatch: MonkeyPatch, tmpdir: Path) -> Iterator[str]:
    """Mock out the environment variables so that we have control over them
    for testing.
    """
    # set the JWKS key id
    monkeypatch.setenv("JWK_KEY_ID", "mock_key")

    # set the jwks path
    MOCK_JWKS_PATH = str(tmpdir.mkdir("keys") / "jwks.json")
    monkeypatch.setenv("JWKS_PATH", MOCK_JWKS_PATH)
    yield MOCK_JWKS_PATH


@pytest.fixture
def with_jwks(jwks_path: str) -> None:
    """Sets up the JWKS file so that it is present during testing"""
    key_id = os.environ["JWK_KEY_ID"]
    jwt_encode.save_jwks(jwt_encode.make_jwks([key_id]))
