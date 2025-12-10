from __future__ import annotations

import time

import colorama
from bs4 import BeautifulSoup

from clients import BrowserSession, CodeforcesClient, SpojClient
from config import DELAY_BETWEEN_DOWNLOADS, RetrieverConfig
from exceptions import RetrieverError
from models import Submission
from storage import DownloadTracker, FileManager
from ui import Console

colorama.init()


class Retriever:

    def __init__(
        self,
        cf_handle: str | None = None,
        cf_password: str | None = None,
        spoj_handle: str | None = None,
        spoj_password: str | None = None,
        codeforces: bool | None = None,
        spoj: bool | None = None,
        get_regular: bool | None = None,
        get_gym: bool | None = None,
        split_gym: bool | None = None,
        folders: bool | None = None,
        verbose: bool = True,
    ) -> None:
        self.config = RetrieverConfig(
            cf_handle=cf_handle,
            cf_password=cf_password,
            spoj_handle=spoj_handle,
            spoj_password=spoj_password,
            download_codeforces=codeforces,
            download_spoj=spoj,
            get_regular=get_regular,
            get_gym=get_gym,
            split_gym=split_gym,
            create_folders=folders,
            verbose=verbose,
        )
        self.ui = Console(verbose=verbose)
        self.file_manager = FileManager()

    def _collect_codeforces_input(self) -> None:
        if self.config.cf_handle is None:
            self.config.cf_handle = self.ui.get_input(
                'Enter your codeforces handle: '
            ).lower()
        else:
            self.config.cf_handle = self.config.cf_handle.lower()

        if self.config.cf_password is None:
            self.config.cf_password = self.ui.get_password(
                f'Enter password for {self.config.cf_handle}: '
            )
        if self.config.get_regular is None:
            self.config.get_regular = self.ui.get_yes_no(
                'Download regular contests submissions? [y/n]: '
            )

        if self.config.get_gym is None:
            self.config.get_gym = self.ui.get_yes_no(
                'Download gym contests submissions? [y/n]: '
            )

        if self.config.split_gym is None:
            if not self.config.get_gym:
                self.config.split_gym = False
            else:
                self.config.split_gym = self.ui.get_yes_no(
                    'Separate regular/gym contests in different folders? [y/n]: '
                )

        if self.config.create_folders is None:
            self.config.create_folders = self.ui.get_yes_no(
                'Create folders separately for each contest? [y/n]: '
            )

    def _collect_spoj_input(self) -> None:
        if self.config.spoj_handle is None:
            self.config.spoj_handle = self.ui.get_input(
                'Enter your spoj username: '
            ).lower()
        else:
            self.config.spoj_handle = self.config.spoj_handle.lower()

        if self.config.spoj_password is None:
            self.config.spoj_password = self.ui.get_password(
                'Enter your spoj password: '
            )

    def _process_codeforces_submissions(
        self,
        cf_client: CodeforcesClient,
        tracker: DownloadTracker,
    ) -> None:
        assert self.config.cf_handle is not None
        assert self.config.create_folders is not None
        submissions_data = cf_client.get_submissions_metadata(self.config.cf_handle)

        for raw_data in submissions_data:
            if 'contestId' not in raw_data:
                raw_data['contestId'] = 'NA'

        total = len(submissions_data)
        for index, raw_data in enumerate(submissions_data, 1):
            try:
                is_gym = raw_data['contestId'] in cf_client.gym_contests
                submission = Submission.from_codeforces_api(
                    raw_data,
                    is_gym=is_gym,
                    handle=self.config.cf_handle,
                    merge_gym=self.config.split_gym is False,
                )
                verdict = submission.get_verdict()
                if verdict and verdict.upper() != 'OK':
                    continue
                if submission.is_gym() and not self.config.get_gym:
                    continue
                if not submission.is_gym() and not self.config.get_regular:
                    continue

                if tracker.is_downloaded(submission.get_problem()):
                    self.ui.print_progress(
                        index,
                        total,
                        f'Skipping (already downloaded) --> {submission}',
                    )
                    continue

                time.sleep(DELAY_BETWEEN_DOWNLOADS)
                self.ui.print_progress(index, total, f'Downloading --> {submission}')

                source_code = cf_client.get_source_code(submission)
                if source_code == '' or source_code is None:
                    self.ui.print_error('Source code fetch failed')
                    tracker.add_error(submission.get_problem())
                    continue

                self.file_manager.save_submission(
                    submission,
                    source_code,
                    create_contest_folder=self.config.create_folders,
                )
                tracker.mark_downloaded(submission.get_problem())

            except Exception as e:
                self.ui.print_error(f'Exception occured:\n{str(e)}')
                problem = raw_data.get('problem', {}).get('index', 'unknown')
                contest_id = raw_data.get('contestId', '')
                if problem != 'unknown':
                    tracker.add_error(f'{contest_id}{problem}')

    def _process_spoj_submissions(
        self,
        client: SpojClient,
        tracker: DownloadTracker,
    ) -> None:
        assert self.config.spoj_handle is not None
        soup = client.get_my_account_page()
        table = soup.find(id='user-profile-tables')
        if table is None:
            return

        table = table.find('table')
        if table is None:
            return

        rows = table.find_all('td')
        for row in rows:
            link_elem = row.find('a')
            if link_elem is None:
                continue

            link = str(link_elem['href'])
            splitted = link.split('/')[2].split(',')

            if (
                len(splitted) == 1
                or splitted[0] in tracker.downloaded
                or splitted[0] == ''
            ):
                continue

            page_soup = client.get_submission_page(link)
            edit_elem = page_soup.find('a', {'title': 'Edit source code'})
            if edit_elem is None:
                continue

            edit_link = str(edit_elem['href'])
            edit_page = client.get_edit_page(edit_link)
            sub_id = edit_link.split('=')[1]
            edit_soup = BeautifulSoup(edit_page, 'html.parser')
            lang_select = edit_soup.find('select', {'name': 'lang'})
            lang = 'Unknown'
            if lang_select:
                selected_opt = lang_select.find('option', {'selected': True})
                if selected_opt:
                    lang = selected_opt.text.strip()
                else:
                    first_opt = lang_select.find('option')
                    if first_opt:
                        lang = first_opt.text.strip()

            submission = Submission.from_spoj(
                {
                    'language': lang,
                    'source': edit_page,
                    'problem': splitted[0],
                    'id': sub_id,
                },
                handle=self.config.spoj_handle,
            )

            self.ui.print_info(f'Downloading --> {submission}')

            source_code = client.get_source_code(submission)
            if source_code:
                self.file_manager.save_submission(submission, source_code)
                tracker.mark_downloaded(submission.get_problem())
            else:
                tracker.add_error(submission.get_problem())

    def _setup_codeforces_directories(self) -> None:
        assert self.config.cf_handle is not None
        base_path = f'codeforces/{self.config.cf_handle}'

        if self.config.get_gym:
            path = f'{base_path}/gym' if self.config.split_gym else base_path
            FileManager.ensure_directory(path)

        if self.config.get_regular:
            path = f'{base_path}/normal' if self.config.split_gym else base_path
            FileManager.ensure_directory(path)

    def _run_codeforces_download(self) -> bool:
        assert self.config.cf_handle is not None
        assert self.config.cf_password is not None

        tracker: DownloadTracker | None = None
        self.ui.print_info(
            f'Downloading codeforces submissions for: {self.config.cf_handle}..'
        )

        with BrowserSession(self.ui) as session:
            try:
                cf_client = CodeforcesClient(session)
                cf_client.load_contest_info()

                tracker = DownloadTracker('codeforces', self.config.cf_handle)
                tracker.load()

                if not cf_client.login(self.config.cf_handle, self.config.cf_password):
                    raise RetrieverError('Invalid handle/password')

                self._setup_codeforces_directories()
                self._process_codeforces_submissions(cf_client, tracker)
                tracker.save()

                if tracker.errors:
                    self.ui.print_info(
                        "Codeforces submissions for the following "
                        "problems weren't downloaded:"
                    )
                    for error in set(tracker.errors):
                        self.ui.print_info(error)
                    retry = self.ui.get_yes_no(
                        f'Run one more time to download the remaining '
                        f'{len(tracker.errors)} submission(s)? [y/n]: '
                    )
                else:
                    retry = False

                self.ui.print_info(
                    f'Done downloading codeforces submissions '
                    f'for: {self.config.cf_handle}'
                )
                return retry

            except RetrieverError as e:
                self.ui.print_error(f'Exception occured:\n{e.get_message()}')
                return False
            except KeyboardInterrupt:
                if tracker is not None:
                    tracker.save()
                self.ui.print_info('Keyboard interrupt (CTRL^C) was pressed, exiting.')
                raise

    def _run_spoj_download(self) -> None:
        assert self.config.spoj_handle is not None
        assert self.config.spoj_password is not None

        self.ui.print_info('Downloading spoj submissions...')
        spoj_tracker: DownloadTracker | None = None

        with BrowserSession(self.ui) as session:
            try:
                spoj_client = SpojClient(session)

                if not spoj_client.login(
                    self.config.spoj_handle, self.config.spoj_password
                ):
                    raise RetrieverError('Invalid username/password')

                spoj_tracker = DownloadTracker('spoj', self.config.spoj_handle)
                spoj_tracker.load()

                self._process_spoj_submissions(spoj_client, spoj_tracker)
                spoj_tracker.save()

                if spoj_tracker.errors:
                    self.ui.print_info(
                        "SPOJ submissions for the following problems "
                        "weren't downloaded:"
                    )
                    for error in set(spoj_tracker.errors):
                        self.ui.print_info(error)
                    self.ui.print_info('Run one more time to download them.')

                self.ui.print_info('Done downloading spoj submissions.')

            except RetrieverError as e:
                self.ui.print_error(f'Exception occured:\n{e.get_message()}')
            except KeyboardInterrupt:
                if spoj_tracker is not None:
                    spoj_tracker.save()
                self.ui.print_info('Keyboard interrupt (CTRL^C) was pressed, exiting.')
                raise

    def _collect_platform_preferences(self) -> None:
        if self.config.download_codeforces is None:
            self.config.download_codeforces = self.ui.get_yes_no(
                'Download codeforces submissions? [y/n]: '
            )

        if self.config.download_codeforces:
            self._collect_codeforces_input()

        if self.config.download_spoj is None:
            self.config.download_spoj = self.ui.get_yes_no(
                'Download spoj submissions? [y/n]: '
            )

        if self.config.download_spoj:
            self._collect_spoj_input()

    def start(self) -> None:
        self._collect_platform_preferences()

        try:
            if self.config.download_codeforces:
                while self._run_codeforces_download():
                    pass

            if self.config.download_spoj:
                self._run_spoj_download()
        except KeyboardInterrupt:
            return
