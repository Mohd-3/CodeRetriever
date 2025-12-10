from __future__ import annotations

import os
from pathlib import Path

import pytest

from models import Platform, Submission
from storage import FileManager


class TestFileManager:
    @pytest.fixture
    def file_manager(self) -> FileManager:
        return FileManager()

    @pytest.fixture
    def temp_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        monkeypatch.chdir(tmp_path)
        return tmp_path

    def test_ensure_directory_creates_path(
        self, file_manager: FileManager, temp_dir: Path
    ) -> None:
        test_path = str(temp_dir / 'new' / 'nested' / 'dir')
        FileManager.ensure_directory(test_path)
        assert os.path.exists(test_path)

    def test_ensure_directory_existing(
        self, file_manager: FileManager, temp_dir: Path
    ) -> None:
        test_path = str(temp_dir / 'existing')
        os.makedirs(test_path)
        FileManager.ensure_directory(test_path)
        assert os.path.exists(test_path)

    def test_save_submission_creates_file(
        self, file_manager: FileManager, temp_dir: Path
    ) -> None:
        submission = Submission(
            platform=Platform.CODEFORCES,
            submission_id=123,
            problem='1234A',
            language='GNU C++17',
            handle='test_user',
            contest_id=1234,
            problem_index='A',
        )

        source_code = '#include <iostream>\nint main() { return 0; }'
        file_path = file_manager.save_submission(submission, source_code)

        assert os.path.exists(file_path)
        with open(file_path) as f:
            content = f.read()
        assert '#include <iostream>' in content

    def test_save_submission_with_contest_folder(
        self, file_manager: FileManager, temp_dir: Path
    ) -> None:
        submission = Submission(
            platform=Platform.CODEFORCES,
            submission_id=123,
            problem='1234A',
            language='GNU C++17',
            handle='test_user',
            contest_id=1234,
            problem_index='A',
        )

        source_code = 'int main() {}'
        file_path = file_manager.save_submission(
            submission, source_code, create_contest_folder=True
        )

        assert '1234' in file_path
        assert os.path.exists(file_path)

    def test_save_submission_normalizes_newlines(
        self, file_manager: FileManager, temp_dir: Path
    ) -> None:
        submission = Submission(
            platform=Platform.SPOJ,
            submission_id='123',
            problem='PRIME1',
            language='Python',
            handle='user',
        )

        source_code = 'line1\r\nline2\r\nline3'
        file_path = file_manager.save_submission(submission, source_code)

        with open(file_path) as f:
            content = f.read()
        assert 'line1\nline2\nline3' in content
