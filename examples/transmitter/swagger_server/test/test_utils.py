# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

import pytest

from swagger_server.utils import get_simple_subject, SimpleSubjectType
from swagger_server.models import Subject, SimpleSubject, ComplexSubject, Aliases, Email, DID, Account, IssSub, Opaque, PhoneNumber, JwtID


@pytest.mark.parametrize("expected_result, class_to_search, subject", [
    # test getting subject types that are present
    [Email(email="user@example.com"), Email,
        Subject.parse_obj({"format": "email", "email": "user@example.com"})],
    [PhoneNumber(phone_number="+12223334444"), PhoneNumber,
        Subject.parse_obj({"format": "phone_number", "phone_number": "+12223334444"})],
    [IssSub(iss="http://issuer.example.com/", sub="145234573"), IssSub,
        Subject.parse_obj({
            "tenant": {"format": "iss_sub", "iss": "http://issuer.example.com/", "sub": "145234573"},
            "user": {"format": "email", "email": "user@example.com"},
            "application": {"format": "opaque", "id": "123456789"}
        })],
    [Opaque(id="123456789"), Opaque,
        Subject.parse_obj({
            "tenant": {"format": "iss_sub", "iss": "http://issuer.example.com/", "sub": "145234573"},
            "user": {"format": "email", "email": "user@example.com"},
            "application": {"format": "opaque", "id": "123456789"}
        })],
    [Account(uri="acct:example.user@service.example.com"), Account,
        Subject.parse_obj({
            "identifiers": [
                {"format": "account", "uri": "acct:example.user@service.example.com"},
                {"format": "did", "url": "did:example:123456/did/url/path?versionId=1"},
                {"format": "email", "email": "user@example.com"},
                {"format": "iss_sub", "iss": "http://issuer.example.com/", "sub": "145234573"},
            ]
        })],
    [DID(url="did:example:123456/did/url/path?versionId=1"), DID,
        Subject.parse_obj({
            "identifiers": [
                {"format": "account", "uri": "acct:example.user@service.example.com"},
                {"format": "did", "url": "did:example:123456/did/url/path?versionId=1"},
                {"format": "email", "email": "user@example.com"},
                {"format": "iss_sub", "iss": "http://issuer.example.com/", "sub": "145234573"},
            ]
        })],
    # test returning None when subject type is not present
    [None, Account,
        Subject.parse_obj({"format": "phone_number", "phone_number": "+12223334444"})],
    [None, DID,
        Subject.parse_obj({
            "tenant": {"format": "iss_sub", "iss": "http://issuer.example.com/", "sub": "145234573"},
            "user": {"format": "email", "email": "user@example.com"},
            "application": {"format": "opaque", "id": "123456789"}
        })],
    [None, JwtID,
        Subject.parse_obj({
            "identifiers": [
                {"format": "account", "uri": "acct:example.user@service.example.com"},
                {"format": "did", "url": "did:example:123456/did/url/path?versionId=1"},
                {"format": "email", "email": "user@example.com"},
                {"format": "iss_sub", "iss": "http://issuer.example.com/", "sub": "145234573"},
            ]
        })],
])
def test_get_simple_subject(
        expected_result: SimpleSubjectType,
        class_to_search: type,
        subject: Subject
    ) -> None:
    assert get_simple_subject(subject, class_to_search) == expected_result


def assert_status_code(response, expected_code: int):
    assert response.status_code == expected_code, (
        f"Incorrect response code: {response.status_code}, "
        f"Response body: {response.data.decode('utf-8')}"
    )