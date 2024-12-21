from fastapi import HTTPException, status


class Abort(Exception):
    def __init__(self, scope: str, message: str):
        self.scope = scope
        self.message = message


class TokenInvalidError(Exception):
    """Custom exception for invalid tokens."""

    def __init__(self, message: str, token_id: str = None, reason: str = None):
        super().__init__(message)
        self.token_id = token_id
        self.reason = reason

    def __str__(self):
        base_message = super().__str__()
        if self.token_id or self.reason:
            return f"{base_message} (Token ID: {self.token_id}, Reason: {self.reason})"
        return base_message


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

