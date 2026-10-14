class ErrorOIDC(RuntimeError):
    def __init__(self, error: str, description: str, status_code: int | None = None) -> None:
        super().__init__(description)
        self.error = error
        self.description = description
        self.status_code = status_code
