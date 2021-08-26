from pathlib import Path

from openid_sse.models.events.caep.session_revoked import SessionRevoked

from helpers.utils import list_examples, load_example
import pytest


TEST_FOLDER = Path(__file__).parent


class TestSessionRevokedExamples:
    @pytest.mark.parametrize(
        "example_file",
        list_examples(TEST_FOLDER, 'session_revoked')
    )
    def test_examples_are_properly_parsed(self, example_file):
        """Ensures that all of the examples in the TEST_FOLDER are
        properly parsed by our pydantic models
        """
        example = load_example(example_file)
        model = SessionRevoked(**example)
        assert example == model.dict(by_alias=True, exclude_none=True)


class TestSessionRevokedInvalid:
    """There are no specific claims attached to the SessionRevoked event,
    so any invalid data should be tested in other modules.
    """
    pass
