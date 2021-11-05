# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

from pathlib import Path
import uuid

from jwcrypto.jwk import JWK, JWKSet
import pytest
import py
from _pytest.monkeypatch import MonkeyPatch

from swagger_server import jwt_encode


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """The function we use to load keys uses LRU Caching to avoid hitting
    the disk too often. We need to clear it before running any unit tests.
    """
    jwt_encode.load_jwks.cache_clear()


class TestMakeJWK:
    @pytest.mark.parametrize(
        "claim",
        ["kty", "alg", "crv", "x", "y", "d", "kid"]
    )
    def test_has_correct_claims(self, claim: str) -> None:
        """Ensures the JWK has all of the expected claims"""
        jwk = jwt_encode.make_jwk(uuid.uuid1().hex)

        assert claim in jwk
        assert isinstance(jwk[claim], str)

    def test_has_correct_values(self) -> None:
        """Ensures the JWK has the expected known values"""
        key_id = uuid.uuid1().hex
        constant_values = dict(
            kty="EC",
            alg="ES256",
            crv="P-256",
            kid=key_id
        )
        jwk = jwt_encode.make_jwk(key_id).export(
            private_key=False, as_dict=True
        )

        # remove non-constant values
        jwk.pop("x")
        jwk.pop("y")

        assert jwk == constant_values


class TestAddJWKToJWKS:
    def test_adds_to_empty_jwks(self) -> None:
        """Ensures we can add a JWK to an empty JWKSet"""
        key_id = uuid.uuid1().hex
        jwks = jwt_encode.make_jwks()
        jwk = jwt_encode.make_jwk(key_id)
        jwt_encode.add_jwk_to_jwks(jwk=jwk, jwks=jwks)
        assert isinstance(jwks.get_key(key_id), JWK)

    def test_adds_to_non_empty_jwks(self) -> None:
        """Ensures we can add a JWK to an empty JWKSet"""
        key_ids = [uuid.uuid1().hex for _ in range(3)]
        jwks = jwt_encode.make_jwks(key_ids)

        key_id = uuid.uuid1().hex
        jwk = jwt_encode.make_jwk(key_id)

        jwt_encode.add_jwk_to_jwks(jwk=jwk, jwks=jwks)

        # check that the new jwk is there
        assert isinstance(jwks.get_key(key_id), JWK)

        # check that the old jwks are there
        for key_id in key_ids:
            assert isinstance(jwks.get_key(key_id), JWK)

    def test_duplicate_errors(self) -> None:
        """Ensure adding a jwk with a kid that is already in the JWKSet
        raises an error"""
        key_id = uuid.uuid1().hex
        jwks = jwt_encode.make_jwks([key_id])

        jwk = jwt_encode.make_jwk(key_id)

        with pytest.raises(ValueError):
            jwt_encode.add_jwk_to_jwks(jwk=jwk, jwks=jwks)


class TestMakeJWKS:
    def test_can_make_single_jwk(self) -> None:
        """Ensures we can create a single JWK in the JWKSet"""
        key_id = uuid.uuid1().hex
        jwks = jwt_encode.make_jwks([key_id])
        assert isinstance(jwks.get_key(key_id), JWK)

    def test_can_make_many_jwks(self) -> None:
        """Ensures we can make many JWKs in a JWKSet"""
        key_ids = [uuid.uuid1().hex for _ in range(5)]
        jwks = jwt_encode.make_jwks(key_ids)

        for kid in key_ids:
            assert isinstance(jwks.get_key(kid), JWK)

    def test_can_make_no_jwks(self) -> None:
        """Ensures we can make an empty JWKSet"""
        jwks = jwt_encode.make_jwks()
        assert isinstance(jwks, JWKSet)

    def test_error_if_duplicate_kid_values(self) -> None:
        """Ensures the kid values are unique in a JWKSet"""
        with pytest.raises(ValueError):
            jwt_encode.make_jwks(["foo", "foo", "foo"])


class TestGetJWKSPath:
    def test_correct_path(self, jwks_path: str) -> None:
        """Ensures we get the expected path"""
        expected = Path(jwks_path)
        actual = jwt_encode.get_jwks_path()

        assert actual == expected


class TestSaveJWKS:
    def test_makes_file(self) -> None:
        """Ensures we are able to save a JWKS file to disk"""
        assert not jwt_encode.get_jwks_path().exists()
        mock_jwks = jwt_encode.make_jwks(["foo", "bar"])
        jwt_encode.save_jwks(mock_jwks)
        assert jwt_encode.get_jwks_path().exists()

    def test_makes_needed_directories(self, monkeypatch: MonkeyPatch, tmpdir: py.path.local) -> None:
        """Ensures the saving process creates all needed directories"""
        temp_base = tmpdir.mkdir("mock")
        monkeypatch.setenv("JWKS_PATH", f"{temp_base}/foo/bar/jwks.json")

        assert not jwt_encode.get_jwks_path().exists()
        mock_jwks = jwt_encode.make_jwks(["foo", "bar"])
        jwt_encode.save_jwks(mock_jwks)
        assert jwt_encode.get_jwks_path().exists()


class TestLoadJWKS:
    def test_loads_jwks(self) -> None:
        """Ensures we are able to load a JWKS file from disk"""
        mock_jwks = jwt_encode.make_jwks(["foo", "bar"])
        jwt_encode.save_jwks(mock_jwks)

        actual = jwt_encode.load_jwks()
        assert actual.export() == mock_jwks.export()


class TestEncodeSet:
    def test_makes_string(self, with_jwks: None) -> None:
        """Ensures we can encode the SET"""

        SET = dict(
            iss="foo",
            aud="bar",
            jti="1234",
            events={
                "https://fake.event.com/account-forgotten": {}
            }
        )

        JWT = jwt_encode.encode_set(SET)
        assert isinstance(JWT, str)


class TestDecodeSet:
    def test_decodes_encoded_set(self, with_jwks: None) -> None:
        jwks = jwt_encode.load_jwks()

        issuer = "foo"
        audience = "bar"

        SET = dict(
            iss=issuer,
            aud=audience,
            jti="1234",
            events={
                "https://fake.event.com/account-forgotten": {}
            }
        )

        JWT = jwt_encode.encode_set(SET)

        actual = jwt_encode.decode_set(JWT, jwks, issuer, audience)

        assert actual == SET
