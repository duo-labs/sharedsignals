# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

from functools import lru_cache
import os
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

from jwcrypto.jwk import JWK, JWKSet
import jwt

from swagger_server.encoder import JSONEncoder
from swagger_server.events import SecurityEvent


def make_jwk(key_id: str) -> JWK:
    """Makes a JSON Web Key with ES256"""
    return JWK.generate(kty="EC", alg="ES256", crv="P-256", kid=key_id)


def add_jwk_to_jwks(jwk: JWK, jwks: JWKSet) -> JWKSet:
    """Adds a JWK as long as it has a kid
    and that kid does not exist in the jwks
    """
    if "kid" not in jwk:
        raise ValueError(
            "A JWK needs a 'kid' claim to distingush it in a JWKSet"
        )

    if jwks.get_key(jwk.kid) is not None:
        raise ValueError(
            f"The 'kid' claim {jwk.kid} is already present in this JWKSet"
        )

    jwks.add(jwk)
    return jwks


def make_jwks(key_ids: Optional[List[str]] = None) -> JWKSet:
    """Makes a JSON Web Key Set with the key_ids passed in"""
    key_ids = [] if key_ids is None else key_ids

    jwks = JWKSet()
    for key_id in key_ids:
        add_jwk_to_jwks(jwk=make_jwk(key_id), jwks=jwks)
    return jwks


def get_jwks_path() -> Path:
    """Get the canonical location for a JWKS file"""
    return Path(os.environ["JWKS_PATH"])


def save_jwks(jwks: JWKSet) -> None:
    """Save a JSON Web Key Set to the appropriate file location"""
    jwks_path = get_jwks_path()
    jwks_path.parent.mkdir(parents=True, exist_ok=True)

    with open(jwks_path, "w") as fout:
        fout.write(jwks.export(private_keys=True))


@lru_cache
def load_jwks() -> JWKSet:
    """Load a JSON Web Key Set from the expected file location"""
    jwks_path = get_jwks_path()
    with open(jwks_path) as fin:
        return JWKSet.from_json(fin.read())


# TODO: make annotation for the SET a pydantic model
def encode_set(security_event_token: SecurityEvent) -> str:
    """This runs on the transmitter. Encodes a SET using EC256"""
    # get the key id of the JWK we want to use
    key_id = os.environ["JWK_KEY_ID"]

    # select the right JWK with the key_id
    jwk = load_jwks().get_key(key_id)
    private_key = jwk.export_to_pem(private_key=True, password=None)

    return jwt.encode(
        payload=security_event_token.dict(exclude_none=True, by_alias=True),
        key=private_key,
        algorithm=jwk.alg,
        headers=dict(
            kid=key_id,
            typ="secevent+jwt"  # https://www.rfc-editor.org/rfc/rfc8417.html#section-2.3
        ),
        json_encoder=JSONEncoder
    )


# TODO: make annotation for the SET a pydantic model
def decode_set(jwt_value: str,
               jwks: Mapping[str, Any],
               iss: Optional[str],
               aud: Union[str, List[str], None]) -> Dict[str, Any]:
    """This runs on the receiver. Decodes a SET intended from a specific issuer
    and for a specific audience
    """
    # get the key id from the header of the JWT
    kid = jwt.get_unverified_header(jwt_value)["kid"]

    # and use it to select the right JWK
    jwk = [jwk for jwk in jwks["keys"] if jwk["kid"] == kid][0]
    key = jwt.PyJWK(jwk).key

    return jwt.decode(
        jwt=jwt_value,
        key=key,
        algorithms=[jwk["alg"]],
        issuer=iss,
        audience=aud
    )
