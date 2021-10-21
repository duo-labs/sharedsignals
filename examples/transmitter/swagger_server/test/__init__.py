# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Licensed under BSD 3-Clause License

import logging
import uuid

import connexion
from flask.testing import FlaskClient
import pytest

from swagger_server.encoder import JSONEncoder
from swagger_server.business_logic.stream import Stream


@pytest.fixture
def client() -> FlaskClient:
    # db_fd, db_path = tempfile.mkstemp()
    # app = create_app({'TESTING': True, 'DATABASE': db_path})
    app = create_app({'TESTING': True})

    with app.test_client() as client:
        # with app.app_context():
        #     init_db()
        yield client

    # os.close(db_fd)
    # os.unlink(db_path)


@pytest.fixture
def new_stream() -> str:
    client_id = uuid.uuid4().hex
    stream = Stream(client_id, "https://test-case.popular-app.com")
    yield stream
    Stream.delete(client_id)


def create_app(self):
    logging.getLogger('connexion.operation').setLevel('ERROR')
    app = connexion.App(__name__, specification_dir='../swagger/')
    app.app.json_encoder = JSONEncoder
    app.add_api('swagger.yaml')
    return app.app
