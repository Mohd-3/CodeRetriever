from dataclasses import dataclass
from typing import Tuple

DELAY_BETWEEN_DOWNLOADS: float = 1.5
DELAY_AFTER_PAGE_FETCH: float = 1.0

CODEFORCES_API_BASE = 'https://codeforces.com/api'
CODEFORCES_SUBMISSION_URL = (
    'http://codeforces.com/{contest_type}/{contest_id}/submission/{submission_id}'
)
CODEFORCES_LOGIN_URL = 'https://codeforces.com/enter'
SPOJ_BASE_URL = 'https://www.spoj.com'

COLOR_FAIL = '\033[91m'
COLOR_ENDC = '\033[0m'

CODEFORCES_EXTENSIONS: Tuple[Tuple[str, str], ...] = (
    ('++', 'cpp'),
    ('GNU C', 'c'),
    ('JavaScript', 'js'),
    ('Java', 'java'),
    ('Py', 'py'),
    ('Delphi', 'dpr'),
    ('FPC', 'pas'),
    ('C#', 'cs'),
    ('D', 'd'),
    ('Q#', 'qs'),
    ('Node', 'js'),
    ('Kotlin', 'kt'),
    ('Go', 'go'),
    ('Ruby', 'rb'),
    ('Rust', 'rs'),
    ('Perl', 'pl'),
    ('Scala', 'scala'),
    ('PascalABC', 'pas'),
    ('Haskell', 'hs'),
    ('PHP', 'php'),
)

SPOJ_EXTENSIONS: Tuple[Tuple[str, str], ...] = (
    ('++', 'cpp'),
    ('gcc', 'c'),
    ('clang', 'c'),
    ('JavaScript', 'js'),
    ('Java', 'java'),
    ('Python', 'py'),
    ('C#', 'cs'),
    ('D ', 'd'),
    ('Node', 'js'),
    ('Kotlin', 'kt'),
    ('Go ', 'go'),
    ('Ruby', 'rb'),
    ('Rust', 'rs'),
    ('Perl', 'pl'),
    ('Scala', 'scala'),
    ('Pascal', 'pas'),
    ('Haskell', 'hs'),
    ('PHP', 'php'),
)


@dataclass
class RetrieverConfig:
    cf_handle: str | None = None
    cf_password: str | None = None
    spoj_handle: str | None = None
    spoj_password: str | None = None
    download_codeforces: bool | None = None
    download_spoj: bool | None = None
    get_regular: bool | None = None
    get_gym: bool | None = None
    split_gym: bool | None = None
    create_folders: bool | None = None
    verbose: bool = True
    delay_between_downloads: float = DELAY_BETWEEN_DOWNLOADS
    delay_after_page_fetch: float = DELAY_AFTER_PAGE_FETCH
