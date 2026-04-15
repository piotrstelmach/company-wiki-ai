from datetime import timedelta, datetime, timezone
import jwt
from fastapi import Depends
from typing import Annotated

from dto.token import GenerateTokenResponse

secret = "your_secret_key_here"

class TokenService:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def generate_token(self, payload: dict, expires: timedelta) -> GenerateTokenResponse:
        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + expires
        to_encode.update({"exp": expire})
        token=jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
        return GenerateTokenResponse(token=token, expires=str(expire))

    def decode_jwt(self, jwt_token: str) -> dict:
        return jwt.decode(jwt_token, self.secret, algorithms=[self.algorithm])

    def refresh_token(self, token: str) -> GenerateTokenResponse | str:
        payload = self.decode_jwt(token)
        expiring_time = payload.get("exp")
        if expiring_time is None:
            return "Invalid token"
        if expiring_time < datetime.now(timezone.utc).timestamp():
            expire_time = timedelta(days=7)
            return self.generate_token(payload, expire_time)

        return token

def get_token_service() -> TokenService:
    return TokenService(secret=secret)

TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]