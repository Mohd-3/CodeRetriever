class RetrieverError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return repr(self.message)

    def get_message(self) -> str:
        return self.message


class AuthenticationError(RetrieverError):
    pass


class APIError(RetrieverError):
    pass


class SourceCodeNotFoundError(RetrieverError):
    pass
