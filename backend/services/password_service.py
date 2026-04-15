from typing import Annotated

from fastapi import Depends
from passlib.context import CryptContext

class PasswordService:
    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)


def get_password_service() -> PasswordService:
    return PasswordService()

PasswordServiceDep = Annotated[PasswordService, Depends(get_password_service)]