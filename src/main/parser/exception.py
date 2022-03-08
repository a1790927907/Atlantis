class ParseException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class ParseServerException(Exception):
    def __init__(self, message, error_code: int = 500):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
