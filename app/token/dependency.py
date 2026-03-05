from .backends import TokenBackend
from settings.config import settings # type: ignore


def get_token_backend() -> TokenBackend:
    """ Dependency to get the token backend """

    return TokenBackend(
        secret_key=settings.JWT_SECRET_KEY, # type: ignore
        algorithm=settings.JWT_ALGORITHM,  # type: ignore
    )