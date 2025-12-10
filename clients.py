from __future__ import annotations

import json
import re
import shutil
import string
import subprocess
import time
from typing import Any, Set, cast

import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

from config import (
    CODEFORCES_API_BASE,
    CODEFORCES_LOGIN_URL,
    CODEFORCES_SUBMISSION_URL,
    DELAY_AFTER_PAGE_FETCH,
    SPOJ_BASE_URL,
)
from exceptions import APIError
from models import Submission
from ui import Console


def _get_chrome_version() -> int | None:
    chrome_paths = [
        'google-chrome',
        'google-chrome-stable',
        'chromium',
        'chromium-browser',
        '/usr/bin/google-chrome',
    ]

    for path in chrome_paths:
        if shutil.which(path) or path.startswith('/'):
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    match = re.search(r'(\d+)\.', result.stdout)
                    if match:
                        return int(match.group(1))
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
    return None


class BrowserResponse:

    def __init__(self, text: str, url: str, status_code: int = 200) -> None:
        self.text = text
        self.url = url
        self.status_code = status_code

    def json(self) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(self.text))


class BrowserSession:

    def __init__(self, ui: Console) -> None:
        self._driver: uc.Chrome | None = None
        self._cookies_valid = False
        self._ui = ui

    def _create_driver(self, headless: bool) -> uc.Chrome:
        chrome_version = _get_chrome_version()
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.page_load_strategy = 'eager'
        if headless:
            options.add_argument('--headless=new')
        return uc.Chrome(options=options, version_main=chrome_version)

    def _ensure_driver(self) -> uc.Chrome:
        if self._driver is None:
            self._driver = self._create_driver(headless=False)
        return self._driver

    def _is_cloudflare_challenge(self) -> bool:
        try:
            if not self._driver:
                return False
            page_source = self._driver.page_source
            title = self._driver.title or ''

            challenge_titles = [
                'Just a moment',
                'Attention Required',
                'Verification',
            ]
            for ct in challenge_titles:
                if ct in title:
                    return True

            if len(title) > 5 and 'Verification' not in title:
                return False

            if len(page_source) < 500:
                return True

            return False
        except Exception:
            return True

    def _after_captcha_solved(self) -> None:
        self._ui.print_info('CAPTCHA solved!')
        time.sleep(3)
        if self._driver:
            self._driver.refresh()
            time.sleep(2)
        self._cookies_valid = True

    def _wait_for_cloudflare(self, url: str, timeout: int = 120) -> None:
        if not self._is_cloudflare_challenge():
            self._cookies_valid = True
            return

        self._ui.print_info('Please solve the CAPTCHA in the browser window...')
        start = time.time()
        while time.time() - start < timeout:
            if not self._is_cloudflare_challenge():
                time.sleep(2)
                self._after_captcha_solved()
                return
            time.sleep(1)
        self._ui.print_error('Warning: Cloudflare wait timeout')

    def get(self, url: str, **kwargs: Any) -> BrowserResponse:
        driver = self._ensure_driver()
        try:
            from selenium.webdriver.common.keys import Keys

            driver.find_element('tag name', 'body').send_keys(Keys.TAB)
        except Exception:
            pass
        driver.get(url)
        self._wait_for_cloudflare(url, timeout=120)
        time.sleep(1)
        return BrowserResponse(driver.page_source, driver.current_url)

    def post(
        self, url: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> BrowserResponse:
        driver = self._ensure_driver()

        if url not in (driver.current_url or ''):
            driver.get(url)
            self._wait_for_cloudflare(url, timeout=120)

        if data:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys

            for name, value in data.items():
                try:
                    field = driver.find_element(By.NAME, name)
                    field.clear()
                    field.send_keys(str(value))
                except Exception:
                    driver.execute_script(
                        "var el = document.querySelector('[name=\"' + arguments[0] + '\"]'); if (el) el.value = arguments[1];",
                        name,
                        str(value),
                    )

            try:
                password_field = driver.find_element(
                    By.CSS_SELECTOR,
                    "input[type='password']",
                )
                password_field.send_keys(Keys.RETURN)
            except Exception:
                driver.execute_script(
                    "var form = document.querySelector('form'); if (form) form.submit();"
                )

            time.sleep(3)
            self._wait_for_cloudflare(url, timeout=120)

        return BrowserResponse(driver.page_source, driver.current_url)

    def minimize(self) -> None:
        if self._driver:
            try:
                self._driver.minimize_window()
            except Exception:
                pass

    def close(self) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None

    def __enter__(self) -> 'BrowserSession':
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class CodeforcesClient:

    def __init__(
        self,
        session: BrowserSession,
        delay_after_fetch: float = DELAY_AFTER_PAGE_FETCH,
    ) -> None:
        self.session = session
        self.delay_after_fetch = delay_after_fetch
        self._gym_contests: Set[int] = set()
        self._regular_contests: Set[int] = set()

    def login(self, handle: str, password: str) -> bool:
        page = self.session.get(CODEFORCES_LOGIN_URL)
        soup = BeautifulSoup(page.text, 'html.parser')
        time.sleep(self.delay_after_fetch)

        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token is None:
            return False

        data = {
            'handleOrEmail': handle,
            'password': password,
            'csrf_token': csrf_token['value'],
            'action': 'enter',
        }
        response = self.session.post(CODEFORCES_LOGIN_URL, data=data)
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup.find('input', {'name': 'handleOrEmail'}) is None

    def load_contest_info(self) -> None:
        for gym_status in ('false', 'true'):
            try:
                response = requests.get(
                    f'{CODEFORCES_API_BASE}/contest.list?gym={gym_status}'
                ).json()
            except (requests.RequestException, ValueError) as exc:
                print(str(exc))
                raise APIError('Error getting contests info.') from exc

            if response['status'] != 'OK':
                print(f'status: {response["status"]}')
                raise APIError('Error getting contests info.')

            for contest in response['result']:
                if gym_status == 'true':
                    self._gym_contests.add(contest['id'])
                else:
                    self._regular_contests.add(contest['id'])

    def is_gym_contest(self, contest_id: int) -> bool:
        return contest_id in self._gym_contests

    def get_submissions_metadata(self, handle: str) -> list[dict[str, Any]]:
        try:
            response = requests.get(
                f'{CODEFORCES_API_BASE}/user.status?handle={handle}'
            ).json()
        except (requests.RequestException, ValueError) as exc:
            raise APIError('Error getting submission info.') from exc

        if response['status'] != 'OK':
            raise APIError('Error getting submission info.')

        return cast(list[dict[str, Any]], response['result'])

    def get_source_code(self, submission: Submission) -> str | None:
        contest_type = 'gym' if submission.is_gym() else 'contest'
        url = CODEFORCES_SUBMISSION_URL.format(
            contest_type=contest_type,
            contest_id=submission.contest_id,
            submission_id=submission.submission_id,
        )

        page = self.session.get(url)
        time.sleep(self.delay_after_fetch)

        soup = BeautifulSoup(page.text, 'html.parser')
        source_element = soup.find(id='program-source-text')

        if source_element is None:
            return None

        lines = source_element.find_all('li')
        if lines:
            source_lines = []
            for li in lines:
                line_text = li.get_text()
                line_text = line_text.replace('\xa0', ' ')
                source_lines.append(line_text)
            source = '\n'.join(source_lines)
        else:
            for br in source_element.find_all('br'):
                br.replace_with('\n')
            source = source_element.get_text()
            source = source.replace('\xa0', ' ')

        printable = set(string.printable)
        return ''.join(c for c in source if c in printable).rstrip()

    @property
    def gym_contests(self) -> Set[int]:
        return self._gym_contests

    @property
    def regular_contests(self) -> Set[int]:
        return self._regular_contests


class SpojClient:

    def __init__(self, session: BrowserSession) -> None:
        self.session = session

    def login(self, handle: str, password: str) -> bool:
        login_url = f'{SPOJ_BASE_URL}/login/'
        data = {
            'next_raw': '/',
            'login_user': handle,
            'password': password,
        }
        self.session.post(login_url, data=data)
        time.sleep(2)
        self.session.get(f'{SPOJ_BASE_URL}/')
        page = self.session.get(f'{SPOJ_BASE_URL}/myaccount')
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup.find('a', {'href': '/login'}) is None

    def get_my_account_page(self) -> BeautifulSoup:
        page = self.session.get(f'{SPOJ_BASE_URL}/myaccount')
        return BeautifulSoup(page.text, 'html.parser')

    def get_submission_page(self, link: str) -> BeautifulSoup:
        page = self.session.get(f'{SPOJ_BASE_URL}{link}')
        return BeautifulSoup(page.text, 'html.parser')

    def get_edit_page(self, edit_link: str) -> str:
        page = self.session.get(f'{SPOJ_BASE_URL}{edit_link}')
        return cast(str, page.text)

    def get_source_code(self, submission: Submission) -> str | None:
        if submission.source is None:
            return None

        soup = BeautifulSoup(submission.source, 'html.parser')
        textarea = soup.find('textarea')
        if textarea:
            return textarea.get_text()

        return None
