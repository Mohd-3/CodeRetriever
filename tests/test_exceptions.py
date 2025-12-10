from __future__ import annotations

import pytest

from exceptions import (
    APIError,
    AuthenticationError,
    RetrieverError,
    SourceCodeNotFoundError,
)


class TestRetrieverError:
    def test_init(self) -> None:
        error = RetrieverError('Test error message')
        assert error.message == 'Test error message'

    def test_str(self) -> None:
        error = RetrieverError('Test error message')
        assert str(error) == "'Test error message'"

    def test_get_message(self) -> None:
        error = RetrieverError('Test error message')
        assert error.get_message() == 'Test error message'

    def test_inheritance(self) -> None:
        error = RetrieverError('Test')
        assert isinstance(error, Exception)


class TestAuthenticationError:
    def test_inheritance(self) -> None:
        error = AuthenticationError('Auth failed')
        assert isinstance(error, RetrieverError)
        assert isinstance(error, Exception)

    def test_message(self) -> None:
        error = AuthenticationError('Invalid credentials')
        assert error.get_message() == 'Invalid credentials'


class TestAPIError:
    def test_inheritance(self) -> None:
        error = APIError('API call failed')
        assert isinstance(error, RetrieverError)

    def test_can_be_raised(self) -> None:
        with pytest.raises(APIError) as exc_info:
            raise APIError('API returned error')
        assert exc_info.value.get_message() == 'API returned error'


class TestSourceCodeNotFoundError:
    def test_inheritance(self) -> None:
        error = SourceCodeNotFoundError('Source not found')
        assert isinstance(error, RetrieverError)
