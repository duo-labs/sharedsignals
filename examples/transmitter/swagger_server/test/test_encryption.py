from pathlib import Path
import uuid

from jwcrypto.jwk import JWK, JWKSet
import pytest

import swagger_server.encryption as enc


@pytest.fixture(autouse=True)
def mock_jwks_path(monkeypatch, tmpdir):
    """Mock out the environment variable so that we have control over it
    for testing.
    """
    MOCK_JWKS_PATH = str(tmpdir.mkdir("keys") / "jwks.json")
    monkeypatch.setenv("JWKS_PATH", MOCK_JWKS_PATH)
    yield MOCK_JWKS_PATH


@pytest.fixture(autouse=True)
def clear_cache():
    """The function we use to load keys uses LRU Caching to avoid hitting
    the disk too often. We need to clear it before running any unit tests.
    """
    enc.load_jwks.cache_clear()


class TestMakeJWK:
    @pytest.mark.parametrize(
        "claim",
        ["kty", "alg", "crv", "x", "y", "d", "kid"]
    )
    def test_has_correct_claims(self, claim):
        """Ensures the JWK has all of the expected claims"""
        jwk = enc.make_jwk(uuid.uuid1().hex)

        assert claim in jwk
        assert isinstance(jwk[claim], str)

    def test_has_correct_values(self):
        """Ensures the JWK has the expected known values"""
        key_id = uuid.uuid1().hex
        constant_values = dict(
            kty="EC",
            alg="ES256",
            crv="P-256",
            kid=key_id
        )
        jwk = enc.make_jwk(key_id).export(private_key=False, as_dict=True)

        # remove non-constant values
        jwk.pop("x")
        jwk.pop("y")

        assert jwk == constant_values


class TestAddJWKToJWKS:
    def test_adds_to_empty_jwks(self):
        """Ensures we can add a JWK to an empty JWKSet"""
        key_id = uuid.uuid1().hex
        jwks = enc.make_jwks()
        jwk = enc.make_jwk(key_id)
        enc.add_jwk_to_jwks(jwk=jwk, jwks=jwks)
        assert isinstance(jwks.get_key(key_id), JWK)

    def test_adds_to_non_empty_jwks(self):
        """Ensures we can add a JWK to an empty JWKSet"""
        key_ids = [uuid.uuid1().hex for _ in range(3)]
        jwks = enc.make_jwks(key_ids)

        key_id = uuid.uuid1().hex
        jwk = enc.make_jwk(key_id)

        enc.add_jwk_to_jwks(jwk=jwk, jwks=jwks)

        # check that the new jwk is there
        assert isinstance(jwks.get_key(key_id), JWK)

        # check that the old jwks are there
        for key_id in key_ids:
            assert isinstance(jwks.get_key(key_id), JWK)

    def test_duplicate_errors(self):
        """Ensure adding a jwk with a kid that is already in the JWKSet
        raises an error"""
        key_id = uuid.uuid1().hex
        jwks = enc.make_jwks([key_id])

        jwk = enc.make_jwk(key_id)

        with pytest.raises(ValueError):
            enc.add_jwk_to_jwks(jwk=jwk, jwks=jwks)


class TestMakeJWKS:
    def test_can_make_single_jwk(self):
        """Ensures we can create a single JWK in the JWKSet"""
        key_id = uuid.uuid1().hex
        jwks = enc.make_jwks([key_id])
        assert isinstance(jwks.get_key(key_id), JWK)

    def test_can_make_many_jwks(self):
        """Ensures we can make many JWKs in a JWKSet"""
        key_ids = [uuid.uuid1().hex for _ in range(5)]
        jwks = enc.make_jwks(key_ids)

        for kid in key_ids:
            assert isinstance(jwks.get_key(kid), JWK)

    def test_can_make_no_jwks(self):
        """Ensures we can make an empty JWKSet"""
        jwks = enc.make_jwks()
        assert isinstance(jwks, JWKSet)

    def test_error_if_duplicate_kid_values(self):
        """Ensures the kid values are unique in a JWKSet"""
        with pytest.raises(ValueError):
            enc.make_jwks(["foo", "foo", "foo"])


class TestGetJWKSPath:
    def test_correct_path(self, mock_jwks_path):
        """Ensures we get the expected path"""
        expected = Path(mock_jwks_path)
        actual = enc.get_jwks_path()

        assert actual == expected


class TestSaveJWKS:
    def test_makes_file(self):
        """Ensures we are able to save a JWKS file to disk"""
        assert not enc.get_jwks_path().exists()
        mock_jwks = enc.make_jwks(["foo", "bar"])
        enc.save_jwks(mock_jwks)
        assert enc.get_jwks_path().exists()


class TestLoadJWKS:
    def test_loads_jwks(self):
        """Ensures we are able to load a JWKS file from disk"""
        mock_jwks = enc.make_jwks(["foo", "bar"])
        enc.save_jwks(mock_jwks)

        actual = enc.load_jwks()
        assert actual.export() == mock_jwks.export()


class TestEncodeSet:
    def test_makes_string(self):
        """Ensures we can encode the SET"""
        key_id = uuid.uuid1().hex
        jwks = enc.make_jwks([key_id])
        enc.save_jwks(jwks)

        SET = dict(
            iss="foo",
            aud="bar",
            jti="1234",
            events={
                "https://fake.event.com/account-forgotten": {}
            }
        )

        JWT = enc.encode_set(SET, key_id)
        assert isinstance(JWT, str)


class TestDecodeSet:
    def test_decodes_encoded_set(self):
        key_id = uuid.uuid1().hex
        jwks = enc.make_jwks([key_id])
        enc.save_jwks(jwks)

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

        JWT = enc.encode_set(SET, key_id)

        actual = enc.decode_set(JWT, jwks, issuer, audience)

        assert actual == SET
