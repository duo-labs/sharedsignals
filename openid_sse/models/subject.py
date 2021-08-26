"""Defines the Subject model described by the draft at
https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers

TODO: update this link once the draft becomes an RFC
"""
from typing import List, Literal, Optional, Text, Union

import pydantic

from openid_sse.models.common import StringOrURI, URI


class Subject(pydantic.BaseModel):
    """https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3  # noqa: E501
    As described in Section 1.2 of SET [RFC8417], subjects related to
    security events may take a variety of forms, including but not
    limited to a JWT [RFC7519] principal, an IP address, a URL, etc.
    Different types of subjects may need to be identified in different
    ways. (e.g., a host might be identified by an IP or MAC address,
    while a user might be identified by an email address) Furthermore,
    even in the case where the type of the subject is known, there may be
    multiple ways by which a given subject may be identified.  For
    example, an account may be identified by an opaque identifier, an
    email address, a phone number, a JWT "iss" claim and "sub" claim,
    etc., depending on the nature and needs of the transmitter and
    receiver.  Even within the context of a given transmitter and
    receiver relationship, it may be appropriate to identify different
    accounts in different ways, for example if some accounts only have
    email addresses associated with them while others only have phone
    numbers.  Therefore it can be necessary to indicate within a SET the
    mechanism by which a subject is being identified.

    To address this problem, this specification defines Subject
    Identifiers - JSON [RFC7159] objects containing information
    identifying a subject - and Identifier Formats - named sets of rules
    describing how to encode different kinds of subject identifying
    information (e.g., an email address, or an issuer and subject pair)
    as a Subject Identifier.
    """
    format: Text


class Account(Subject):
    """https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.1  # noqa: E501
    The Account Identifier Format identifies a subject using an account
    at a service provider, identified with an "acct" URI as defined in
    [RFC7565].  Subject Identifiers in this format MUST contain a "uri"
    member whose value is the "acct" URI for the subject.  The "uri"
    member is REQUIRED and MUST NOT be null or empty.  The Account
    Identifier Format is identified by the name "account".
    """
    format: Literal["account"] = "account"
    uri: URI


class DID(Subject):
    """https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.3  # noqa: E501
    The Decentralized Identifier Format identifies a subject using a
    Decentralized Identifier (DID) URL as defined in [DID].  Subject
    Identifiers in this format MUST contain a "url" member whose value is
    a DID URL for the DID Subject being identified.  The value of the
    "url" member MUST be a valid DID URL and MAY be a bare DID.  The
    "url" member is REQUIRED and MUST NOT be null or empty.  The
    Decentralized Identifier Format is identified by the name "did".
    """
    format: Literal["did"] = "did"
    # TODO: complete


class Email(Subject):
    """https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.4  # noqa: E501
    The Email Identifier Format identifies a subject using an email
    address.  Subject Identifiers in this format MUST contain an "email"
    member whose value is a string containing the email address of the
    subject, formatted as an "addr-spec" as defined in Section 3.4.1 of
    [RFC5322].  The "email" member is REQUIRED and MUST NOT be null or
    empty.  The value of the "email" member SHOULD identify a mailbox to
    which email may be delivered, in accordance with [RFC5321].  The
    Email Identifier Format is identified by the name "email".
    """
    format: Literal["email"] = "email"
    # TODO: complete


class IssSub(Subject):
    """https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.5  # noqa: E501
    The Issuer and Subject Identifier Format identifies a subject using a
    pair of "iss" and "sub" members, analagous to how subjects are
    identified using the "iss" and "sub" claims in OpenID Connect
    [OpenID.Core] ID Tokens.  These members MUST follow the formats of
    the "iss" member and "sub" member defined by [RFC7519], respectively.
    Both the "iss" member and the "sub" member are REQUIRED and MUST NOT
    be null or empty.  The Issuer and Subject Identifier Format is
    identified by the name "iss_sub".
    """
    format: Literal["iss_sub"] = "iss_sub"
    iss: StringOrURI
    sub: Text


class JwtID(Subject):
    """https://openid.net/specs/openid-sse-framework-1_0-01.html#rfc.section.3.4.1  # noqa: E501
    The "JWT ID" Subject Identifier Format specifies a JSON Web Token (JWT)
    identifier, defined in [RFC7519].
    """
    format: Literal["jwt_id"] = "jwt_id"
    # TODO: complete


class Opaque(Subject):
    """https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.6  # noqa: E501
    The Opaque Identifier Format describes a subject that is identified
    with a string with no semantics asserted beyond its usage as an
    identifier for the subject, such as a UUID or hash used as a
    surrogate identifier for a record in a database.  Subject Identifiers
    in this format MUST contain an "id" member whose value is a JSON
    string containing the opaque string identifier for the subject.  The
    "id" member is REQUIRED and MUST NOT be null or empty.  The Opaque
    Identifier Format is identified by the name "opaque".
    """
    format: Literal["opaque"] = "opaque"
    id: Text


class PhoneNumber(Subject):
    """https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.7  # noqa: E501
    The Phone Number Identifier Format identifies a subject using a
    telephone number.  Subject Identifiers in this format MUST contain a
    "phone_number" member whose value is a string containing the full
    telephone number of the subject, including international dialing
    prefix, formatted according to E.164 [E164].  The "phone_number"
    member is REQUIRED and MUST NOT be null or empty.  The Phone Number
    Identifier Format is identified by the name "phone_number".
    """
    format: Literal["phone_number"] = "phone_number"
    # TODO: complete


class SamlAssertionID(Subject):
    """https://openid.net/specs/openid-sse-framework-1_0-01.html#rfc.section.3.4.2  # noqa: E501
    The "SAML Assertion ID" Subject Identifier Format specifies a SAML 2.0
    [OASIS.saml-core-2.0-os] assertion identifier.
    """
    format: Literal["saml_assertion_id"] = "saml_assertion_id"
    # TODO: complete


# Use this as the type for any simple subject
ANY_SIMPLE_SUBJECT = Union[
    Account,
    DID,
    Email,
    IssSub,
    JwtID,
    Opaque,
    PhoneNumber,
    SamlAssertionID
]


class Aliases(Subject):
    """https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.2  # noqa: E501
    The Aliases Identifier Format describes a subject that is identified
    with a list of different Subject Identifiers.  It is intended for use
    when a variety of identifiers have been shared with the party that
    will be interpreting the Subject Identifier, and it is unknown which
    of those identifiers they will recognize or support.  Subject
    Identifiers in this format MUST contain an "identifiers" member whose
    value is a JSON array containing one or more Subject Identifiers.
    Each Subject Identifier in the array MUST identify the same entity.
    The "identifiers" member is REQUIRED and MUST NOT be null or empty.
    It MAY contain multiple instances of the same Identifier Format
    (e.g., multiple Email Subject Identifiers), but SHOULD NOT contain
    exact duplicates.  This format is identified by the name "aliases".

    "alias" Subject Identifiers MUST NOT be nested; i.e., the
    "identifiers" member of an "alias" Subject Identifier MUST NOT
    contain a Subject Identifier in the "aliases" format.
    """
    format: Literal["aliases"] = "aliases"
    identifiers: List[ANY_SIMPLE_SUBJECT] = pydantic.Field(..., min_items=1)

    @pydantic.validator('identifiers', allow_reuse=True)
    def ensure_not_nested(cls, v):
        for subject in v:
            if isinstance(subject, cls):
                raise TypeError(
                    "Cannot use Aliases format as an identifier for an "
                    "Aliases subject"
                )

        return v


class ComplexSubject(pydantic.BaseModel):
    """https://openid.net/specs/openid-sse-framework-1_0-01.html#rfc.section.3.2  # noqa: E501
    A Complex Subject Member has a name and a value that is a JSON object that
    has one or more Simple Subject Members.
    """
    user: Optional[ANY_SIMPLE_SUBJECT]
    device: Optional[ANY_SIMPLE_SUBJECT]
    session: Optional[ANY_SIMPLE_SUBJECT]
    application: Optional[ANY_SIMPLE_SUBJECT]
    tenant: Optional[ANY_SIMPLE_SUBJECT]
    org_unit: Optional[ANY_SIMPLE_SUBJECT]
    group: Optional[ANY_SIMPLE_SUBJECT]

    @pydantic.root_validator()
    def at_least_one_field(cls, values):
        """Ensures that at least one of the optional fields is defined"""
        if not any(values.values()):
            raise ValueError("At least one attribute must be included")

        return values


# use this as the type for any subject
ANY_SUBJECT = Union[ComplexSubject, Aliases, ANY_SIMPLE_SUBJECT]
