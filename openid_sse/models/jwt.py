"""Defines the JWT model described by RFC 7519:
https://datatracker.ietf.org/doc/html/rfc7519
"""
from typing import Optional, Sequence, Text, Union

import pydantic

from openid_sse.models.common import StringOrURI


# NOTE: Explicitly type the SET in header
# https://openid.net/specs/openid-sse-framework-1_0.html#rfc.section.11.1.4


class JWT(pydantic.BaseModel):
    """
    https://datatracker.ietf.org/doc/html/rfc7519#section-3
    JSON Web Token (JWT) is a compact, URL-safe means of representing
    claims to be transferred between two parties.  The claims in a JWT
    are encoded as a JSON object that is used as the payload of a JSON
    Web Signature (JWS) structure or as the plaintext of a JSON Web
    Encryption (JWE) structure, enabling the claims to be digitally
    signed or integrity protected with a Message Authentication Code
    (MAC) and/or encrypted.

    The JWT defined in this package is further restricted to only apply to
    SETs as defined in the SSE standards:

    1. https://openid.net/specs/openid-sse-framework-1_0.html#rfc.section.11.1.2  # noqa: E501
    The JWT sub claim MUST NOT be present in any SET containing a SSE event.

    2. https://openid.net/specs/openid-sse-framework-1_0.html#rfc.section.11.1.5  # noqa: E501
    The exp claim MUST NOT be used in SSE SETs.

    3. https://datatracker.ietf.org/doc/html/rfc8417#section-2.2
    iss, iat, and jti are REQUIRED
    """
    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.1
    # The "iss" (issuer) claim identifies the principal that issued the
    # JWT.  The processing of this claim is generally application specific.
    # The "iss" value is a case-sensitive string containing a StringOrURI
    # value.
    iss: StringOrURI

    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3
    # The "aud" (audience) claim identifies the recipients that the JWT is
    # intended for.  Each principal intended to process the JWT MUST
    # identify itself with a value in the audience claim.  If the principal
    # processing the claim does not identify itself with a value in the
    # "aud" claim when this claim is present, then the JWT MUST be
    # rejected.  In the general case, the "aud" value is an array of case-
    # sensitive strings, each containing a StringOrURI value.  In the
    # special case when the JWT has one audience, the "aud" value MAY be a
    # single case-sensitive string containing a StringOrURI value.  The
    # interpretation of audience values is generally application specific.
    # Use of this claim is OPTIONAL.
    aud: Optional[Union[Sequence[StringOrURI], StringOrURI]]

    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.5
    # The "nbf" (not before) claim identifies the time before which the JWT
    # MUST NOT be accepted for processing.  The processing of the "nbf"
    # claim requires that the current date/time MUST be after or equal to
    # the not-before date/time listed in the "nbf" claim.  Implementers MAY
    # provide for some small leeway, usually no more than a few minutes, to
    # account for clock skew.  Its value MUST be a number containing a
    # NumericDate value.  Use of this claim is OPTIONAL.
    nbf: Optional[int]

    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.6
    # The "iat" (issued at) claim identifies the time at which the JWT was
    # issued.  This claim can be used to determine the age of the JWT.  Its
    # value MUST be a number containing a NumericDate value.
    iat: int

    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.7
    # The "jti" (JWT ID) claim provides a unique identifier for the JWT.
    # The identifier value MUST be assigned in a manner that ensures that
    # there is a negligible probability that the same value will be
    # accidentally assigned to a different data object; if the application
    # uses multiple issuers, collisions MUST be prevented among values
    # produced by different issuers as well.  The "jti" claim can be used
    # to prevent the JWT from being replayed.  The "jti" value is a case-
    # sensitive string.
    jti: Text
