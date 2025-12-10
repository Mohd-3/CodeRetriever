from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from config import CODEFORCES_EXTENSIONS, SPOJ_EXTENSIONS


class Platform(Enum):
    CODEFORCES = 'codeforces'
    SPOJ = 'spoj'


class ContestType(Enum):
    REGULAR = 'contest'
    GYM = 'gym'


@dataclass
class Submission:
    platform: Platform
    submission_id: int | str
    problem: str
    language: str
    handle: str
    contest_id: int | str | None = None
    problem_index: str | None = None
    creation_time: int | None = None
    verdict: str | None = None
    contest_type: ContestType | None = None
    source: str | None = None
    merge_gym: bool = True
    extension: str = field(init=False)

    def __post_init__(self) -> None:
        self.extension = self._determine_extension()

    def _determine_extension(self) -> str:
        extensions = (
            SPOJ_EXTENSIONS if self.platform == Platform.SPOJ else CODEFORCES_EXTENSIONS
        )
        for key, value in extensions:
            if key in self.language:
                return value
        return ''

    @classmethod
    def from_codeforces_api(
        cls,
        raw_data: dict[str, Any],
        is_gym: bool,
        handle: str,
        merge_gym: bool,
    ) -> Submission:
        contest_id = raw_data.get('contestId', 'NA')
        problem_index = raw_data['problem']['index']
        return cls(
            platform=Platform.CODEFORCES,
            submission_id=raw_data['id'],
            problem=f'{contest_id}{problem_index}',
            language=raw_data['programmingLanguage'],
            handle=handle,
            contest_id=contest_id,
            problem_index=problem_index,
            creation_time=raw_data.get('creationTimeSeconds'),
            verdict=raw_data.get('verdict'),
            contest_type=ContestType.GYM if is_gym else ContestType.REGULAR,
            merge_gym=merge_gym,
        )

    @classmethod
    def from_spoj(
        cls,
        raw_data: dict[str, Any],
        handle: str,
    ) -> Submission:
        return cls(
            platform=Platform.SPOJ,
            submission_id=raw_data['id'],
            problem=raw_data['problem'],
            language=raw_data['language'],
            handle=handle,
            source=raw_data.get('source'),
        )

    def get_id(self) -> int | str:
        return self.submission_id

    def get_directory(self) -> str:
        base = os.path.join(self.platform.value, self.handle)
        if self.platform == Platform.CODEFORCES and not self.merge_gym:
            subdir = 'gym' if self.contest_type == ContestType.GYM else 'normal'
            return os.path.join(base, subdir)
        return base

    def get_filename(self) -> str:
        if self.platform == Platform.CODEFORCES:
            return f'{self.problem_index}.{self.extension}'
        return f'{self.problem}.{self.extension}'

    def get_path(self) -> str:
        return self.get_filename()

    def get_creation_datetime(self) -> datetime | None:
        if self.creation_time is not None:
            return datetime.fromtimestamp(self.creation_time)
        return None

    def get_creation_time(self) -> datetime | None:
        return self.get_creation_datetime()

    def get_contest(self) -> int | str | None:
        return self.contest_id

    def get_language(self) -> str:
        return self.language

    def get_verdict(self) -> str | None:
        return self.verdict

    def get_index(self) -> str | None:
        return self.problem_index

    def get_problem(self) -> str:
        return self.problem

    def is_gym(self) -> bool:
        return self.contest_type == ContestType.GYM

    def __str__(self) -> str:
        if self.platform == Platform.CODEFORCES:
            return (
                f'Platform: Codeforces, Submission: {self.get_id()}, '
                f'Contest: {self.get_contest()}, Problem: {self.get_index()}, '
                f'Verdict: {self.get_verdict()}, When: {self.get_creation_datetime()}'
            )
        return (
            f'Platform: SPOJ, Submission: {self.get_id()}, '
            f'Problem: {self.get_problem()}'
        )
