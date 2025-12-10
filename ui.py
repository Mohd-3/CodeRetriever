from __future__ import annotations

from getpass import getpass

from config import COLOR_ENDC, COLOR_FAIL


class Console:

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    def get_yes_no(self, message: str) -> bool:
        while True:
            response = input(message).lower()
            if response in ('y', 'n'):
                return response == 'y'

    def get_input(self, message: str) -> str:
        return input(message)

    def get_password(self, message: str) -> str:
        return getpass(message)

    def print_info(self, message: str) -> None:
        if self.verbose:
            print(message)

    def print_error(self, message: str) -> None:
        if self.verbose:
            print(f'{COLOR_FAIL}{message}{COLOR_ENDC}')

    def print_progress(self, current: int, total: int, message: str) -> None:
        if self.verbose:
            print(f'[{current}/{total}] {message}')
