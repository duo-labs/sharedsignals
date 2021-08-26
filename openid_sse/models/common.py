"""Module for common types and validators"""
import re
from typing import Text

from pydantic.networks import url_regex

URN_REGEX = r"urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+"
URL_REGEX = url_regex().pattern
URI_REGEX = re.compile(f"^({URN_REGEX})|({URL_REGEX})$", re.IGNORECASE)


class URI(Text):
    """A pydantic field that validates that the string is either
    a URN or a URL
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattern=URI_REGEX.pattern,
            examples=[
                "https://www.duosecurity.com",
                "urn:this:is:my:identifier"
            ],
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            v_type = type(v)
            raise TypeError(f"URI must be a string. Got {v_type} instead")

        if not URI_REGEX.match(v):
            raise ValueError(f"{v} is not a valid URI")

        return v


class StringOrURI(str):
    """A pydantic field that allows any string,
    but if the string contains a ':' it must be a URI
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples=[
                "foo",
                "https://www.duosecurity.com",
                "urn:this:is:my:identifier"
            ],
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            v_type = type(v)
            raise TypeError(
                f"StringOrURI must be a string. Got {v_type} instead"
            )

        if ":" in v and not URI_REGEX.match(v):
            raise ValueError(f"{v} contains a colon, but is not a valid URI")

        return v


class Message(dict):
    """Represents a message in potentially many languages. Enforces non-empty
    dictionary.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples=[
                {"en": "This is a message.", "es": "Este es un mensaje."},
                {"en-US": "This is a message, dude."},
            ],
        )

    @classmethod
    def validate(cls, v):
        if not len(v) >= 1:
            raise TypeError(
                "A Message must include at least one (language tag, text) pair"
            )

        # TODO: Should we use regex or a package like
        # https://github.com/rspeer/langcodes to validate
        # that the language tags are correct?

        return v
