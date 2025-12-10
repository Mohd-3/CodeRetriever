from __future__ import annotations

import os
from typing import Set

from models import Submission


class FileManager:

    @staticmethod
    def ensure_directory(path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    def save_submission(
        self,
        submission: Submission,
        source_code: str,
        create_contest_folder: bool = False,
    ) -> str:
        directory = submission.get_directory()

        if create_contest_folder and submission.contest_id:
            directory = os.path.join(directory, str(submission.contest_id))

        self.ensure_directory(directory)

        if create_contest_folder:
            filename = submission.get_filename()
        else:
            filename = f'{submission.problem}.{submission.extension}'

        file_path = os.path.join(directory, filename)

        with open(file_path, 'w') as f:
            f.write('\n'.join(source_code.splitlines()))

        return file_path


class DownloadTracker:

    def __init__(self, platform: str, handle: str) -> None:
        self.base_path = os.path.join(platform, handle)
        self.tracker_path = os.path.join(self.base_path, 'downloaded')
        self.errors_path = os.path.join(self.base_path, 'errors')
        self._downloaded: Set[str] = set()
        self._errors: list[str] = []

    def load(self) -> Set[str]:
        FileManager.ensure_directory(self.base_path)
        if os.path.exists(self.tracker_path):
            with open(self.tracker_path, 'r') as f:
                self._downloaded = set(f.read().splitlines())
        else:
            self._downloaded = set()
        return self._downloaded

    def save(self) -> None:
        with open(self.tracker_path, 'w') as f:
            for problem in self._downloaded:
                f.write(f'{problem}\n')

        if self._errors:
            with open(self.errors_path, 'w') as f:
                for error in self._errors:
                    f.write(f'{error}\n')

    def mark_downloaded(self, problem: str) -> None:
        self._downloaded.add(problem)

    def is_downloaded(self, problem: str) -> bool:
        return problem in self._downloaded

    def add_error(self, problem: str) -> None:
        self._errors.append(problem)

    @property
    def downloaded(self) -> Set[str]:
        return self._downloaded

    @property
    def errors(self) -> list[str]:
        return self._errors
