#!/usr/bin/env python3
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a
# BSD 3-Clause License that can be found in the LICENSE file.

import connexion

from swagger_server import encoder
from logging.config import dictConfig


def _init_logging():
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


def main():
    _init_logging()
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml',
                arguments={'title': 'Stream Management API for OpenID Shared Security Events'},
                pythonic_params=True)
    app.run(port=443, ssl_context='adhoc', host='0.0.0.0')


if __name__ == '__main__':
    main()
