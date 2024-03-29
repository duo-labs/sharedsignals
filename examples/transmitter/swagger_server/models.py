# generated by datamodel-codegen:
#   filename:  swagger.yaml

from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, Extra, Field, constr


class Status(Enum):
    """
        REQUIRED. The status of the stream. Values can be one of:

    enabled:
      The Transmitter MUST transmit events over the stream,
      according to the stream’s configured delivery method.

    paused:
      The Transmitter MUST NOT transmit events over the stream.
      The transmitter will hold any events it would have transmitted while paused,
      and SHOULD transmit them when the stream’s status becomes enabled.
      If a Transmitter holds successive events that affect the same Subject Principal,
      then the Transmitter MUST make sure that those events are transmitted in
      the order of time that they were generated OR the Transmitter MUST send
      only the last events that do not require the previous events affecting
      the same Subject Principal to be processed by the Receiver,
      because the previous events are either cancelled by the later events or
      the previous events are outdated.

    disabled:
      The Transmitter MUST NOT transmit events over the stream,
      and will not hold any events for later transmission.
    """

    enabled = 'enabled'
    paused = 'paused'
    disabled = 'disabled'


class TransmitterConfiguration(BaseModel):
    """
        Transmitters have metadata describing their configuration.
    [OpenID Spec](https://openid.net/specs/openid-sse-framework-1_0.html#discovery-meta)

    """

    issuer: AnyUrl = Field(
        ...,
        description='URL using the https scheme with no query or fragment component that the Transmitter asserts as its\nIssuer Identifier.\nThis MUST be identical to the iss claim value in Security Event Tokens issued from this Transmitter.\n',
        example='https://most-secure.com',
    )
    jwks_uri: AnyUrl = Field(
        ...,
        description="URL of the Transmitter's [JSON Web Key Set](https://openid.net/specs/openid-sse-framework-1_0.html#RFC7517)\ndocument. This contains the signing key(s) the Receiver uses to validate signatures from the Transmitter.\n",
        example='https://transmitter.most-secure.com/jwks.json',
    )
    delivery_methods_supported: Optional[List[AnyUrl]] = Field(
        None,
        description='List of supported delivery method URIs. Recommended.',
        example=[
            'https://schemas.openid.net/secevent/risc/delivery-method/push',
            'https://schemas.openid.net/secevent/risc/delivery-method/poll',
        ],
    )
    configuration_endpoint: Optional[AnyUrl] = Field(
        None,
        description='The URL of the Configuration Endpoint.',
        example='https://transmitter.most-secure.com/stream',
    )
    status_endpoint: Optional[AnyUrl] = Field(
        None,
        description='The URL of the Status Endpoint.',
        example='https://transmitter.most-secure.com/status',
    )
    add_subject_endpoint: Optional[AnyUrl] = Field(
        None,
        description='The URL of the Add Subject Endpoint.',
        example='https://transmitter.most-secure.com/add-subject',
    )
    remove_subject_endpoint: Optional[AnyUrl] = Field(
        None,
        description='The URL of the Remove Subject Endpoint.',
        example='https://transmitter.most-secure.com/remove-subject',
    )
    verification_endpoint: Optional[AnyUrl] = Field(
        None,
        description='The URL of the Verification Endpoint.',
        example='https://transmitter.most-secure.com/verification',
    )
    critical_subject_members: Optional[List[str]] = Field(
        None,
        description='List of member names in a Complex Subject which, if present in a Subject Member in an event,\nMUST be interpreted by a Receiver.\n',
        example=['tenant', 'user'],
    )


class PollDeliveryMethod(BaseModel):
    method: Literal[
        'https://schemas.openid.net/secevent/risc/delivery-method/poll'
    ] = 'https://schemas.openid.net/secevent/risc/delivery-method/poll'
    endpoint_url: Optional[AnyUrl] = Field(
        None,
        description='The URL where events can be retrieved from. This is specified by the Transmitter.',
    )


class PushDeliveryMethod(BaseModel):
    method: Literal[
        'https://schemas.openid.net/secevent/risc/delivery-method/push'
    ] = 'https://schemas.openid.net/secevent/risc/delivery-method/push'
    endpoint_url: AnyUrl = Field(
        ...,
        description='The URL where events are pushed through HTTP POST. This is set by the Receiver.',
    )
    authorization_header: Optional[str] = Field(
        None,
        description='The HTTP Authorization header that the Transmitter MUST set with each event delivery,\nif the configuration is present. The value is optional and it is set by the Receiver.',
    )


class RegisterResponse(BaseModel):
    token: str = Field(
        ...,
        description='The Bearer Token that the receiver will need to use for all Stream Management API calls that require authorization.',
    )


class EventType(Enum):
    """
    Supports all [RISC](https://openid.net/specs/openid-risc-profile-specification-1_0-01.html) and [CAEP](https://openid.net/specs/openid-caep-specification-1_0-ID1.html) event types.
    """

    session_revoked = 'session-revoked'
    token_claims_change = 'token-claims-change'
    credential_change = 'credential-change'
    assurance_level_change = 'assurance-level-change'
    device_compliance_change = 'device-compliance-change'
    account_purged = 'account-purged'
    account_disabled = 'account-disabled'
    account_enabled = 'account-enabled'
    identifier_changed = 'identifier-changed'
    identifier_recycled = 'identifier-recycled'
    credential_compromise = 'credential-compromise'
    opt_in = 'opt-in'
    opt_out_initiated = 'opt-out-initiated'
    opt_out_cancelled = 'opt-out-cancelled'
    opt_out_effective = 'opt-out-effective'
    recovery_activated = 'recovery-activated'
    recovery_information_changed = 'recovery-information-changed'


class PollParameters(BaseModel):
    maxEvents: Optional[int] = Field(
        None,
        description='An OPTIONAL integer value indicating the maximum number of unacknowledged SETs to be returned.\nThe SET Transmitter SHOULD NOT send more SETs than the specified maximum.\nIf more than the maximum number of SETs are available, the SET Transmitter determines which to return first;\nthe oldest SETs available MAY be returned first, or another selection algorithm MAY be used,\nsuch as prioritizing SETs in some manner that makes sense for the use case.\nA value of 0 MAY be used by SET Recipients that would like to perform an acknowledge-only request.\nThis enables the Recipient to use separate HTTP requests for acknowledgement and reception of SETs.\nIf this parameter is omitted, no limit is placed on the number of SETs to be returned.',
    )
    returnImmediately: Optional[bool] = Field(
        None,
        description='An OPTIONAL JSON boolean value that indicates the SET Transmitter SHOULD return an immediate response even if no\nresults are available (short polling). The default value is false, which indicates the request is to be treated\nas an HTTP long poll, per [Section 2](https://www.rfc-editor.org/rfc/rfc6202#section-2) of\n[RFC6202](https://www.rfc-editor.org/rfc/rfc8936.html#RFC6202).\nThe timeout for the request is part of the configuration between the participants, which is out of scope of this specification.',
    )
    acks: Optional[List[str]] = Field(
        None,
        description='List of event JTIs that the receiver is acknowledging. The Transmitter can stop keeping track of these.',
    )


class RegisterParameters(BaseModel):
    audience: Optional[AnyUrl] = Field(
        None,
        description='The audience claim to be used for all events on this stream.',
        example='https://popular-app.com',
    )


class VerificationParameters(BaseModel):
    state: Optional[str] = Field(
        None,
        description='OPTIONAL. An arbitrary string that the Event Transmitter\nMUST echo back to the Event Receiver in the verification\nevent’s payload. Event Receivers MAY use the value of this\nparameter to correlate a verification event with a\nverification request. If the verification event is\ninitiated by the transmitter then this parameter MUST not\nbe set.\n',
    )


class Account(BaseModel):
    """
        [Spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.1)

    The Account Identifier Format identifies a subject using an account
    at a service provider, identified with an "acct" URI as defined in
    [RFC7565](https://datatracker.ietf.org/doc/html/rfc7565).
    Subject Identifiers in this format MUST contain a "uri"
    member whose value is the "acct" URI for the subject.  The "uri"
    member is REQUIRED and MUST NOT be null or empty.  The Account
    Identifier Format is identified by the name "account".
    """

    format: Literal['account'] = Field('account', title='Format')
    uri: constr(regex=r'^acct:[^\s]+$') = Field(
        ..., example='acct:reginold@popular-app.com', title='Uri'
    )


class DID(BaseModel):
    """
        [Spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.3)

    The Decentralized Identifier Format identifies a subject using a
    Decentralized Identifier (DID) URL as defined in [DID](https://www.w3.org/TR/did-core/).
    Subject Identifiers in this format MUST contain a "url" member whose value is
    a DID URL for the DID Subject being identified.  The value of the
    "url" member MUST be a valid DID URL and MAY be a bare DID.  The
    "url" member is REQUIRED and MUST NOT be null or empty.  The
    Decentralized Identifier Format is identified by the name "did".
    """

    format: Literal['did'] = Field('did', title='Format')
    url: constr(regex=r'^did:[^\s]+$') = Field(
        ..., example='did:example:123456/did/url/path?versionId=1', title='Url'
    )


class Email(BaseModel):
    """
        [Spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.4)

    The Email Identifier Format identifies a subject using an email
    address.  Subject Identifiers in this format MUST contain an "email"
    member whose value is a string containing the email address of the
    subject, formatted as an "addr-spec" as defined in Section 3.4.1 of
    [RFC5322](https://datatracker.ietf.org/doc/html/rfc5322).
    The "email" member is REQUIRED and MUST NOT be null or
    empty.  The value of the "email" member SHOULD identify a mailbox to
    which email may be delivered, in accordance with [RFC5321](https://datatracker.ietf.org/doc/html/rfc5321).
    The Email Identifier Format is identified by the name "email".
    """

    format: Literal['email'] = Field('email', title='Format')
    email: constr(
        regex=r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
    ) = Field(..., example='reginold@popular-app.com', title='Email')


class IssSub(BaseModel):
    """
        [Spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.5)

    The Issuer and Subject Identifier Format identifies a subject using a
    pair of "iss" and "sub" members, analagous to how subjects are
    identified using the "iss" and "sub" claims in OpenID Connect
    [OpenID.Core](http://openid.net/specs/openid-connect-core-1_0.html) ID Tokens.
    These members MUST follow the formats of the "iss" member and "sub" member
    defined by [RFC7519](https://datatracker.ietf.org/doc/html/rfc7519), respectively.
    Both the "iss" member and the "sub" member are REQUIRED and MUST NOT
    be null or empty.  The Issuer and Subject Identifier Format is
    identified by the name "iss_sub".
    """

    format: Literal['iss_sub'] = Field('iss_sub', title='Format')
    iss: str = Field(..., example='https://most-secure.com', title='iss')
    sub: str = Field(..., example='145234573', title='sub')


class JwtID(BaseModel):
    """
        [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#rfc.section.3.4.1)

    The "JWT ID" Subject Identifier Format specifies a JSON Web Token (JWT)
    identifier, defined in [RFC7519](https://datatracker.ietf.org/doc/html/rfc7519).
    """

    format: Literal['jwt_id'] = Field('jwt_id', title='Format')
    iss: str = Field(
        ...,
        description='The "iss" (issuer) claim of the JWT being identified, defined in\n[RFC7519](https://datatracker.ietf.org/doc/html/rfc7519)',
        example='https://most-secure.com',
        title='iss',
    )
    jti: str = Field(
        ...,
        description='The "jti" (JWT token ID) claim of the JWT being identified, defined in\n[RFC7519](https://datatracker.ietf.org/doc/html/rfc7519)',
        example='B70BA622-9515-4353-A866-823539EECBC8',
        title='jti',
    )


class Opaque(BaseModel):
    """
        [Spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.6)

    The Opaque Identifier Format describes a subject that is identified
    with a string with no semantics asserted beyond its usage as an
    identifier for the subject, such as a UUID or hash used as a
    surrogate identifier for a record in a database.  Subject Identifiers
    in this format MUST contain an "id" member whose value is a JSON
    string containing the opaque string identifier for the subject.  The
    "id" member is REQUIRED and MUST NOT be null or empty.  The Opaque
    Identifier Format is identified by the name "opaque".
    """

    format: Literal['opaque'] = Field('opaque', title='Format')
    id: str = Field(..., example='11112222333344445555', title='Id')


class PhoneNumber(BaseModel):
    """
        [Spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.7)

    The Phone Number Identifier Format identifies a subject using a
    telephone number.  Subject Identifiers in this format MUST contain a
    "phone_number" member whose value is a string containing the full
    telephone number of the subject, including international dialing
    prefix, formatted according to E.164
    [E164](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#ref-E164).
    The "phone_number" member is REQUIRED and MUST NOT be null or empty.
    The Phone Number Identifier Format is identified by the name "phone_number".
    """

    format: Literal['phone_number'] = Field('phone_number', title='Format')
    phone_number: str = Field(..., example=12065550100, title='Phone Number')


class SamlAssertionID(BaseModel):
    """
        [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#rfc.section.3.4.2)

    The "SAML Assertion ID" Subject Identifier Format specifies a SAML 2.0
    [OASIS.saml-core-2.0-os](https://openid.net/specs/openid-sse-framework-1_0.html#OASIS.saml-core-2.0-os)
    assertion identifier.
    """

    format: Literal['saml_assertion_id'] = Field('saml_assertion_id', title='Format')
    issuer: str = Field(
        ...,
        description='The "Issuer" value of the SAML assertion being identified, defined in\n[OASIS.saml-core-2.0-os](https://openid.net/specs/openid-sse-framework-1_0.html#OASIS.saml-core-2.0-os)',
        example='https://most-secure.com',
        title='Issuer',
    )
    assertion_id: str = Field(
        ...,
        description='The "ID" value of the SAML assertion being identified, defined in\n[OASIS.saml-core-2.0-os](https://openid.net/specs/openid-sse-framework-1_0.html#OASIS.saml-core-2.0-os)',
        example='_8e8dc5f69a98cc4c1ff3427e5ce34606fd672f91e6',
        title='Assertion ID',
    )


class SimpleSubject(BaseModel):
    __root__: Union[
        Account, DID, Email, IssSub, JwtID, Opaque, PhoneNumber, SamlAssertionID
    ] = Field(..., discriminator={'propertyName': 'format'}, title='Simple Subject')


class Aliases(BaseModel):
    """
        [Spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3.2.2)

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
    contain a Subject Identifier in the "aliases" format.'
    """

    format: Literal['aliases'] = Field('aliases', title='Format')
    identifiers: List[SimpleSubject] = Field(..., min_items=1)


class ComplexSubject(BaseModel):
    """
        [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#rfc.section.3.2)

    A Complex Subject Member has a name and a value that is a JSON object that
    has one or more Simple Subject Members. All members within a Complex Subject
    MUST represent attributes of the same Subject Principal.
    As a whole, the Complex Subject MUST refer to exactly one Subject Principal.
    """

    class Config:
        extra = Extra.forbid

    application: Optional[SimpleSubject] = None
    device: Optional[SimpleSubject] = None
    group: Optional[SimpleSubject] = None
    org_unit: Optional[SimpleSubject] = None
    session: Optional[SimpleSubject] = None
    tenant: Optional[SimpleSubject] = None
    user: Optional[SimpleSubject] = None


class Subject(BaseModel):
    __root__: Union[SimpleSubject, Aliases, ComplexSubject] = Field(
        ...,
        description='[Spec](https://datatracker.ietf.org/doc/html/draft-ietf-secevent-subject-identifiers#section-3)\n\nAs described in Section 1.2 of SET [RFC8417](https://datatracker.ietf.org/doc/html/rfc8417),\nsubjects related to security events may take a variety of forms,\nincluding but not limited to a JWT [RFC7519](https://datatracker.ietf.org/doc/html/rfc7519)\nprincipal, an IP address, a URL, etc. Different types of subjects may need\nto be identified in different ways. (e.g., a host might be identified by an\nIP or MAC address, while a user might be identified by an email address)\nFurthermore, even in the case where the type of the subject is known,\nthere may be multiple ways by which a given subject may be identified.\nFor example, an account may be identified by an opaque identifier, an\nemail address, a phone number, a JWT "iss" claim and "sub" claim,\netc., depending on the nature and needs of the transmitter and\nreceiver.  Even within the context of a given transmitter and\nreceiver relationship, it may be appropriate to identify different\naccounts in different ways, for example if some accounts only have\nemail addresses associated with them while others only have phone\nnumbers.  Therefore it can be necessary to indicate within a SET the\nmechanism by which a subject is being identified.\n\nTo address this problem, this specification defines Subject\nIdentifiers - JSON [RFC7519](https://datatracker.ietf.org/doc/html/rfc7519)\nobjects containing information identifying a subject - and Identifier Formats -\nnamed sets of rules describing how to encode different kinds of subject\nidentifying information (e.g., an email address, or an issuer and subject pair)\nas a Subject Identifier.',
        discriminator={'propertyName': 'format'},
    )


class Error(BaseModel):
    code: str
    message: str


class StreamStatus(BaseModel):
    status: Status = Field(
        ...,
        description='REQUIRED. The status of the stream. Values can be one of:\n\nenabled:\n  The Transmitter MUST transmit events over the stream,\n  according to the stream’s configured delivery method.\n\npaused:\n  The Transmitter MUST NOT transmit events over the stream.\n  The transmitter will hold any events it would have transmitted while paused,\n  and SHOULD transmit them when the stream’s status becomes enabled.\n  If a Transmitter holds successive events that affect the same Subject Principal,\n  then the Transmitter MUST make sure that those events are transmitted in\n  the order of time that they were generated OR the Transmitter MUST send\n  only the last events that do not require the previous events affecting\n  the same Subject Principal to be processed by the Receiver,\n  because the previous events are either cancelled by the later events or\n  the previous events are outdated.\n\ndisabled:\n  The Transmitter MUST NOT transmit events over the stream,\n  and will not hold any events for later transmission.',
        example='disabled',
    )
    subject: Optional[Subject] = Field(
        None,
        description='OPTIONAL. The Subject to which the status applies.',
        example={'format': 'email', 'email': 'reginold@popular-app.com'},
    )


class StreamConfiguration(BaseModel):
    """
        JSON Object describing and Event Stream's configuration
    [Spec](https://openid.net/specs/openid-sse-framework-1_0.html#stream-config)"

    """

    iss: Optional[AnyUrl] = Field(
        None,
        description='Read-Only.\nA URL using the https scheme with no query or fragment component that the Transmitter asserts as its Issuer\nIdentifier. This MUST be identical to the iss Claim value in Security Event Tokens issued from this Transmitter.',
        example='https://most-secure.com',
    )
    aud: Optional[Union[AnyUrl, List[AnyUrl]]] = Field(
        None,
        description='Read-Only.\nA string or an array of strings containing an audience claim as defined in\n[JSON Web Token (JWT)](https://openid.net/specs/openid-sse-framework-1_0.html#RFC7519) that identifies\nthe Event Receiver(s) for the Event Stream. This property cannot be updated. If multiple Receivers are specified\nthen the Transmitter SHOULD know that these Receivers are the same entity.',
        example='https://popular-app.com',
    )
    events_supported: Optional[List[AnyUrl]] = Field(
        None,
        description='Read-Only.\nAn array of URIs identifying the set of events supported by the Transmitter for this Receiver.\nIf omitted, Event Transmitters SHOULD make this set available to the Event Receiver via some other means\n(e.g. publishing it in online documentation).',
        example=[
            'https://schemas.openid.net/secevent/caep/event-type/session-revoked',
            'https://schemas.openid.net/secevent/risc/event-type/credential-compromise',
        ],
    )
    events_requested: List[AnyUrl] = Field(
        ...,
        description='Read-Write.\nAn array of URIs identifying the set of events that the Receiver requested.\nA Receiver SHOULD request only the events that it understands and it can act on.\nThis is configurable by the Receiver.',
        example=[
            'https://schemas.openid.net/secevent/risc/event-type/credential-compromise'
        ],
    )
    events_delivered: Optional[List[AnyUrl]] = Field(
        None,
        description='Read-Only.\nAn array of URIs which is the intersection of events_supported and events_requested.\nThese events MAY be delivered over the Event Stream.',
        example=[
            'https://schemas.openid.net/secevent/risc/event-type/credential-compromise'
        ],
    )
    delivery: Union[PushDeliveryMethod, PollDeliveryMethod] = Field(
        ...,
        description='Read-Write.\nA JSON object containing a set of name/value pairs specifying configuration parameters for the SET delivery\nmethod. The actual delivery method is identified by the special key method with the value being a URI as defined\nin [Section 11.2.1](https://openid.net/specs/openid-sse-framework-1_0.html#delivery-meta).',
        discriminator={'propertyName': 'method'},
        example={
            'method': 'https://schemas.openid.net/secevent/risc/delivery-method/poll',
            'endpoint_url': None,
        },
    )
    min_verification_interval: Optional[int] = Field(
        None,
        description='Read-Only.\nAn integer indicating the minimum amount of time in seconds that must pass in between verification requests.\nIf an Event Receiver submits verification requests more frequently than this, the Event Transmitter MAY respond\nwith a 429 status code. An Event Transmitter SHOULD NOT respond with a 429 status code if an Event Receiver is not\nexceeding this frequency.',
    )
    format: Optional[str] = Field(
        None,
        description='Read-Write.\nThe Subject Identifier Format that the Receiver wants for the events.\nIf not set then the Transmitter might decide to use a type that discloses more information than necessary.',
    )


class UpdateStreamStatus(StreamStatus):
    reason: Optional[str] = Field(
        None,
        description='OPTIONAL. A short text description that explains the reason for the change.',
        example='Disabled by administrator action.',
    )


class TriggerEventParameters(BaseModel):
    """
    JSON Object describing request to create a security event to test SSE receiver/transmitter

    """

    event_type: EventType = Field(
        ...,
        description='Supports all [RISC](https://openid.net/specs/openid-risc-profile-specification-1_0-01.html) and [CAEP](https://openid.net/specs/openid-caep-specification-1_0-ID1.html) event types.',
        example='credential-compromise',
    )
    subject: Subject


class AddSubjectParameters(BaseModel):
    subject: Subject
    verified: Optional[bool] = Field(
        None,
        description='OPTIONAL. A boolean value; when true, it indicates that the Event Receiver has verified the Subject claim.\nWhen false, it indicates that the Event Receiver has not verified the Subject claim.\nIf omitted, Event Transmitters SHOULD assume that the subject has been verified.',
    )


class RemoveSubjectParameters(BaseModel):
    subject: Subject
