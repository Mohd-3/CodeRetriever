from __future__ import annotations

from typing import Any

import pytest

from models import ContestType, Platform, Submission


class TestSubmission:
    def test_from_codeforces_api_regular_contest(
        self, sample_codeforces_submission: dict[str, Any]
    ) -> None:
        submission = Submission.from_codeforces_api(
            raw_data=sample_codeforces_submission,
            is_gym=False,
            handle='test_user',
            merge_gym=False,
        )

        assert submission.platform == Platform.CODEFORCES
        assert submission.submission_id == 123456789
        assert submission.contest_id == 1234
        assert submission.problem_index == 'A'
        assert submission.problem == '1234A'
        assert submission.extension == 'cpp'
        assert submission.contest_type == ContestType.REGULAR
        assert submission.is_gym() is False

    def test_from_codeforces_api_gym_contest(
        self, sample_codeforces_submission: dict[str, Any]
    ) -> None:
        sample_codeforces_submission['contestId'] = 100001
        sample_codeforces_submission['programmingLanguage'] = 'Python 3'

        submission = Submission.from_codeforces_api(
            raw_data=sample_codeforces_submission,
            is_gym=True,
            handle='test_user',
            merge_gym=False,
        )

        assert submission.contest_type == ContestType.GYM
        assert submission.is_gym() is True
        assert submission.extension == 'py'

    def test_from_spoj(self, sample_spoj_submission: dict[str, Any]) -> None:
        submission = Submission.from_spoj(
            raw_data=sample_spoj_submission, handle='spoj_user'
        )

        assert submission.platform == Platform.SPOJ
        assert submission.problem == 'PRIME1'
        assert submission.extension == 'py'

    @pytest.mark.parametrize(
        'language,expected_ext',
        [
            ('GNU C++17', 'cpp'),
            ('GNU C++14', 'cpp'),
            ('GNU C11', 'c'),
            ('Python 3', 'py'),
            ('PyPy 3', 'py'),
            ('Java 11', 'java'),
            ('Kotlin 1.4', 'kt'),
            ('Go 1.15', 'go'),
            ('Rust 1.49', 'rs'),
            ('JavaScript', 'js'),
            ('Node.js', 'js'),
            ('C# Mono', 'cs'),
            ('Unknown Language', ''),  # Should default to empty
        ],
    )
    def test_extension_mapping(self, language: str, expected_ext: str) -> None:
        raw_data = {
            'id': 1,
            'contestId': 1,
            'problem': {'index': 'A'},
            'programmingLanguage': language,
            'verdict': 'OK',
            'creationTimeSeconds': 1609459200,
        }

        submission = Submission.from_codeforces_api(
            raw_data=raw_data,
            is_gym=False,
            handle='user',
            merge_gym=True,
        )

        assert submission.extension == expected_ext

    def test_get_directory_codeforces_merged(
        self, sample_codeforces_submission: dict[str, Any]
    ) -> None:
        submission = Submission.from_codeforces_api(
            raw_data=sample_codeforces_submission,
            is_gym=False,
            handle='user',
            merge_gym=True,
        )

        assert submission.get_directory() == 'codeforces/user'

    def test_get_directory_codeforces_split_regular(
        self, sample_codeforces_submission: dict[str, Any]
    ) -> None:
        submission = Submission.from_codeforces_api(
            raw_data=sample_codeforces_submission,
            is_gym=False,
            handle='user',
            merge_gym=False,
        )

        assert submission.get_directory() == 'codeforces/user/normal'

    def test_get_directory_codeforces_split_gym(
        self, sample_codeforces_submission: dict[str, Any]
    ) -> None:
        submission = Submission.from_codeforces_api(
            raw_data=sample_codeforces_submission,
            is_gym=True,
            handle='user',
            merge_gym=False,
        )

        assert submission.get_directory() == 'codeforces/user/gym'

    def test_get_directory_spoj(self, sample_spoj_submission: dict[str, Any]) -> None:
        submission = Submission.from_spoj(
            raw_data=sample_spoj_submission, handle='user'
        )

        assert submission.get_directory() == 'spoj/user'

    def test_get_filename_codeforces(
        self, sample_codeforces_submission: dict[str, Any]
    ) -> None:
        submission = Submission.from_codeforces_api(
            raw_data=sample_codeforces_submission,
            is_gym=False,
            handle='user',
            merge_gym=True,
        )

        assert submission.get_filename() == 'A.cpp'

    def test_get_filename_spoj(self, sample_spoj_submission: dict[str, Any]) -> None:
        submission = Submission.from_spoj(
            raw_data=sample_spoj_submission, handle='user'
        )

        assert submission.get_filename() == 'PRIME1.py'

    def test_str_codeforces(self, sample_codeforces_submission: dict[str, Any]) -> None:
        submission = Submission.from_codeforces_api(
            raw_data=sample_codeforces_submission,
            is_gym=False,
            handle='user',
            merge_gym=True,
        )

        result = str(submission)
        assert 'Platform: Codeforces' in result
        assert 'Submission: 123456789' in result
        assert 'Contest: 1234' in result

    def test_str_spoj(self, sample_spoj_submission: dict[str, Any]) -> None:
        submission = Submission.from_spoj(
            raw_data=sample_spoj_submission, handle='user'
        )

        result = str(submission)
        assert 'Platform: SPOJ' in result
        assert 'Problem: PRIME1' in result
