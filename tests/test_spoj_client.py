from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from clients import SpojClient
from models import Platform, Submission


class TestSpojClient:
    @pytest.fixture
    def mock_session(self) -> MagicMock:
        return MagicMock(spec=requests.Session)

    @pytest.fixture
    def client(self, mock_session: MagicMock) -> SpojClient:
        return SpojClient(mock_session)

    def test_login_success(self, client: SpojClient, mock_session: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.text = '<html><body>Welcome user</body></html>'
        mock_session.get.return_value = mock_response

        result = client.login('test_user', 'password')

        assert result is True
        mock_session.post.assert_called_once()

    def test_login_failure(self, client: SpojClient, mock_session: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.text = '<html><a href="/login">Login</a></html>'
        mock_session.get.return_value = mock_response

        result = client.login('test_user', 'wrong_password')

        assert result is False

    def test_get_my_account_page(
        self, client: SpojClient, mock_session: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.text = '<html><body>Account page</body></html>'
        mock_session.get.return_value = mock_response

        soup = client.get_my_account_page()

        assert soup is not None
        assert 'Account page' in soup.text

    def test_get_source_code_success(self, client: SpojClient) -> None:
        submission = Submission(
            platform=Platform.SPOJ,
            submission_id='123',
            problem='PRIME1',
            language='Python',
            handle='user',
            source='<html><textarea id="source">print("hello")\nprint("world")</textarea></html>',
        )

        source = client.get_source_code(submission)

        assert source is not None
        assert 'print("hello")' in source

    def test_get_source_code_no_source(self, client: SpojClient) -> None:
        submission = Submission(
            platform=Platform.SPOJ,
            submission_id='123',
            problem='PRIME1',
            language='Python',
            handle='user',
            source=None,
        )

        source = client.get_source_code(submission)

        assert source is None

    def test_get_source_code_no_textarea(self, client: SpojClient) -> None:
        submission = Submission(
            platform=Platform.SPOJ,
            submission_id='123',
            problem='PRIME1',
            language='Python',
            handle='user',
            source='<html><body>Page without source</body></html>',
        )

        source = client.get_source_code(submission)

        assert source is None or source == ''
