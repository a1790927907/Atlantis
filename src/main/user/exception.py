class UserServerException(Exception):
    def __init__(self, message: str, error_code: int = 500, **kwargs):
        self.message = message
        self.error_code = error_code
        self.kwargs = kwargs
        super().__init__(message, error_code)
