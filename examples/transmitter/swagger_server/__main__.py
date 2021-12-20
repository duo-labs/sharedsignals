#!/usr/bin/env python3
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
from logging.config import dictConfig
import os

import connexion

from swagger_server import encoder
from swagger_server import db
from swagger_server import jwt_encode
from swagger_server.errors import register_error_handlers
from logging.config import dictConfig


def _init_logging() -> None:
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'DEBUG',
            'handlers': ['wsgi']
        }
    })


def main() -> None:
    _init_logging()

    db.create(drop=False)

    make_keys()

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        'swagger.yaml',
        arguments={
            'title': 'Stream Management API for OpenID Shared Security Events'
        },
        pythonic_params=True
    )

    register_error_handlers(app)

    app.run(port=443, ssl_context='adhoc', host='0.0.0.0')


def make_keys() -> None:
    """Makes a JWKS.json file
    with a generated key for JWK_KEY_ID if it doesn't exist
    """
    # load or create the JWKSet
    try:
        jwks = jwt_encode.load_jwks()
    except FileNotFoundError:
        jwks = jwt_encode.make_jwks([])

    key_id = os.environ["JWK_KEY_ID"]

    # generate and add the key if not there already
    if not jwks.get_key(key_id):
        jwk = jwt_encode.make_jwk(key_id)
        jwt_encode.add_jwk_to_jwks(jwk, jwks)

    # and save it
    jwt_encode.save_jwks(jwks)


if __name__ == '__main__':
    main()
