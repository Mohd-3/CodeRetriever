from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture
def sample_codeforces_submission() -> dict[str, Any]:
    return {
        'id': 123456789,
        'contestId': 1234,
        'creationTimeSeconds': 1609459200,
        'problem': {'contestId': 1234, 'index': 'A', 'name': 'Test Problem'},
        'programmingLanguage': 'GNU C++17',
        'verdict': 'OK',
        'testset': 'TESTS',
        'passedTestCount': 10,
    }


@pytest.fixture
def sample_spoj_submission() -> dict[str, Any]:
    return {
        'id': 'spoj123',
        'problem': 'PRIME1',
        'language': 'Python 3 (python 3.8)',
        'source': '<textarea id="source">print("hello")</textarea>',
    }
