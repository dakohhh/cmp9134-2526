import jwt
from settings.config import settings
from datetime import datetime, timezone
from app.token.tokens import Token, TokenType, AccessToken, RefreshToken
from app.token.exception import TokenBackendError
from .utils import get_current_time


ALLOWED_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]

class TokenBackend:
    def __init__(
            self, 
            *,
            secret_key: str, 
            algorithm: str,
        ) -> None:
        self._validate_algorithm(algorithm)

        self.secret_key = secret_key
        self.algorithm = algorithm

    def _validate_algorithm(self, algorithm: str)-> None:
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBackendError(f"Invalid algorithm: {self.algorithm}. Allowed algorithms are: {ALLOWED_ALGORITHMS}")

    def encode_token(self, token: Token) -> str:

        payload = token.model_dump()

        token_string = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )
        return token_string

    def decode_token(self, token: str, verify: bool = True)-> Token:
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm], 
                options={"verify_signature": verify},
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenBackendError("Token expired")
        except jwt.InvalidTokenError as e:
            raise TokenBackendError(f"Invalid token: {e}")

        exp = payload.get("exp")
        
        if exp:
            current_time = get_current_time()
            expired_token_time = datetime.fromtimestamp(exp, timezone.utc)

            if expired_token_time < current_time:
                raise TokenBackendError("Token expired")

        # Return the correct token type based on the type claim
        if payload.get("type") == TokenType.REFRESH.value:
            return RefreshToken(**payload)
        elif payload.get("type") == TokenType.ACCESS.value:
            return AccessToken(**payload)
        else:
            raise TokenBackendError(f"Invalid token type: {payload.get('type')}")
        

def get_token_backend() -> TokenBackend:
    """ Dependency to get the token backend """

    return TokenBackend(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )