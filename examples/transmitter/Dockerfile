# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

FROM python:3.9

ENV JWKS_PATH /usr/keys/jwks.json
ENV JWK_KEY_ID transmitter-ES256-001

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 443

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
