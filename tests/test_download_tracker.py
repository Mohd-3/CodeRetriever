from __future__ import annotations

import os
from pathlib import Path

import pytest

from storage import DownloadTracker


class TestDownloadTracker:

    @pytest.fixture
    def temp_dir(self, tmp_path: Path) -> Path:
        return tmp_path

    @pytest.fixture
    def tracker(
        self,
        temp_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> DownloadTracker:
        monkeypatch.chdir(temp_dir)
        return DownloadTracker('codeforces', 'test_user')

    def test_load_creates_directory(
        self,
        tracker: DownloadTracker,
        temp_dir: Path,
    ) -> None:
        tracker.load()
        assert os.path.exists(temp_dir / 'codeforces' / 'test_user')

    def test_load_empty_when_no_file(self, tracker: DownloadTracker) -> None:
        downloaded = tracker.load()
        assert downloaded == set()

    def test_load_reads_existing_file(
        self, tracker: DownloadTracker, temp_dir: Path
    ) -> None:
        dir_path = temp_dir / 'codeforces' / 'test_user'
        os.makedirs(dir_path)
        with open(dir_path / 'downloaded', 'w') as f:
            f.write('1234A\n1234B\n5678C\n')

        downloaded = tracker.load()

        assert downloaded == {'1234A', '1234B', '5678C'}

    def test_mark_downloaded(self, tracker: DownloadTracker) -> None:
        tracker.load()
        tracker.mark_downloaded('1234A')

        assert tracker.is_downloaded('1234A')
        assert not tracker.is_downloaded('1234B')

    def test_save_writes_file(self, tracker: DownloadTracker, temp_dir: Path) -> None:
        tracker.load()
        tracker.mark_downloaded('1234A')
        tracker.mark_downloaded('1234B')
        tracker.save()

        with open(temp_dir / 'codeforces' / 'test_user' / 'downloaded') as f:
            content = f.read().splitlines()

        assert set(content) == {'1234A', '1234B'}

    def test_save_writes_errors(self, tracker: DownloadTracker, temp_dir: Path) -> None:
        tracker.load()
        tracker.add_error('5678C')
        tracker.add_error('5678D')
        tracker.save()

        with open(temp_dir / 'codeforces' / 'test_user' / 'errors') as f:
            content = f.read().splitlines()

        assert content == ['5678C', '5678D']

    def test_downloaded_property(self, tracker: DownloadTracker) -> None:
        tracker.load()
        tracker.mark_downloaded('1234A')

        assert '1234A' in tracker.downloaded

    def test_errors_property(self, tracker: DownloadTracker) -> None:
        tracker.load()
        tracker.add_error('5678C')

        assert tracker.errors == ['5678C']
