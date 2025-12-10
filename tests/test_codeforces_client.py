from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from clients import CodeforcesClient
from exceptions import APIError
from models import ContestType, Platform, Submission

SAMPLE_SUBMISSION_HTML = '''<!DOCTYPE html>
<html>
<head><title>Submission</title></head>
<body>
<pre id="program-source-text">
#include &lt;iostream&gt;
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << n * 2 << endl;
    return 0;
}
</pre>
</body>
</html>
'''


class TestCodeforcesClient:

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        return MagicMock(spec=requests.Session)

    @pytest.fixture
    def client(self, mock_session: MagicMock) -> CodeforcesClient:
        return CodeforcesClient(mock_session, delay_after_fetch=0)

    @patch('clients.requests.get')
    def test_load_contest_info_success(
        self,
        mock_requests_get: MagicMock,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        mock_requests_get.return_value.json.side_effect = [
            {'status': 'OK', 'result': [{'id': 1234}, {'id': 5678}]},
            {'status': 'OK', 'result': [{'id': 100001}, {'id': 100002}]},
        ]

        client.load_contest_info()

        assert client.is_gym_contest(100001) is True
        assert client.is_gym_contest(100002) is True
        assert client.is_gym_contest(1234) is False
        assert client.is_gym_contest(5678) is False

    @patch('clients.requests.get')
    def test_load_contest_info_api_error(
        self,
        mock_requests_get: MagicMock,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        mock_requests_get.return_value.json.return_value = {
            'status': 'FAILED',
            'comment': 'Error',
        }

        with pytest.raises(APIError):
            client.load_contest_info()

    @patch('clients.requests.get')
    def test_get_submissions_metadata_success(
        self,
        mock_requests_get: MagicMock,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        mock_requests_get.return_value.json.return_value = {
            'status': 'OK',
            'result': [
                {'id': 123, 'contestId': 1234, 'verdict': 'OK'},
                {'id': 456, 'contestId': 1234, 'verdict': 'WRONG_ANSWER'},
            ],
        }

        result = client.get_submissions_metadata('test_user')

        assert len(result) == 2
        assert result[0]['id'] == 123
        assert result[1]['verdict'] == 'WRONG_ANSWER'

    @patch('clients.requests.get')
    def test_get_submissions_metadata_api_error(
        self,
        mock_requests_get: MagicMock,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        mock_requests_get.return_value.json.return_value = {
            'status': 'FAILED',
            'comment': 'User not found',
        }

        with pytest.raises(APIError):
            client.get_submissions_metadata('nonexistent_user')

    def test_get_source_code_success(
        self,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        mock_session.get.return_value.text = SAMPLE_SUBMISSION_HTML

        submission = Submission(
            platform=Platform.CODEFORCES,
            submission_id=56789,
            problem='1234A',
            language='GNU C++17',
            handle='user',
            contest_id=1234,
            problem_index='A',
            contest_type=ContestType.REGULAR,
        )

        source = client.get_source_code(submission)

        assert source is not None
        assert 'int main' in source

    def test_get_source_code_not_found(
        self,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        mock_session.get.return_value.text = '<html><body>No source here</body></html>'

        submission = Submission(
            platform=Platform.CODEFORCES,
            submission_id=56789,
            problem='1234A',
            language='GNU C++17',
            handle='user',
            contest_id=1234,
            problem_index='A',
            contest_type=ContestType.REGULAR,
        )

        source = client.get_source_code(submission)

        assert source is None

    def test_login_success(
        self,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        first_response = MagicMock()
        first_response.text = "<html><input name='csrf_token' value='abc123'/></html>"

        second_response = MagicMock()
        second_response.text = '<html><body>Welcome</body></html>'

        mock_session.get.return_value = first_response
        mock_session.post.return_value = second_response

        result = client.login('user', 'password')

        assert result is True

    def test_login_failure(
        self,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        first_response = MagicMock()
        first_response.text = "<html><input name='csrf_token' value='abc123'/></html>"

        second_response = MagicMock()
        second_response.text = "<html><input name='handleOrEmail' value=''/></html>"

        mock_session.get.return_value = first_response
        mock_session.post.return_value = second_response

        result = client.login('user', 'wrong_password')

        assert result is False

    @patch('clients.requests.get')
    def test_gym_contests_property(
        self,
        mock_requests_get: MagicMock,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        mock_requests_get.return_value.json.side_effect = [
            {'status': 'OK', 'result': []},
            {'status': 'OK', 'result': [{'id': 100001}]},
        ]

        client.load_contest_info()

        assert 100001 in client.gym_contests

    @patch('clients.requests.get')
    def test_regular_contests_property(
        self,
        mock_requests_get: MagicMock,
        client: CodeforcesClient,
        mock_session: MagicMock,
    ) -> None:
        mock_requests_get.return_value.json.side_effect = [
            {'status': 'OK', 'result': [{'id': 1234}]},
            {'status': 'OK', 'result': []},
        ]

        client.load_contest_info()

        assert 1234 in client.regular_contests
