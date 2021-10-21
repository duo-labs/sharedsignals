import logging
from typing import Iterator
import uuid

import connexion
from flask.testing import FlaskClient
import pytest

from swagger_server.encoder import JSONEncoder
from swagger_server.business_logic.stream import Stream


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    app = create_app({'TESTING': True})

    with app.test_client() as client:
        yield client


@pytest.fixture
def new_stream() -> Iterator[Stream]:
    client_id = uuid.uuid4().hex
    stream = Stream(client_id=client_id)
    yield stream
    Stream.delete(client_id)


def create_app(self):
    logging.getLogger('connexion.operation').setLevel('ERROR')
    app = connexion.App(__name__, specification_dir='../swagger/')
    app.app.json_encoder = JSONEncoder
    app.add_api('swagger.yaml')
    return app.app
