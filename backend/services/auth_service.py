import uuid
from datetime import timedelta

from fastapi import Depends
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from database import db_connection
from dto.user import UserCreateSchema, UserAuthResponse
from models import User, RefreshToken
from .token_service import get_token_service, TokenService
from .password_service import get_password_service, PasswordService
from exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    UsernameAlreadyExistsError,
    InvalidTokenError,
    TokenRevokedError
)


class AuthService:
    def __init__(self,
                 database: Session = Depends(db_connection),
                 password_service: PasswordService = Depends(get_password_service),
                 token_service: TokenService = Depends(get_token_service)) -> None:
        self.database = database
        self.password_service = password_service
        self.token_service = token_service

    def _create_auth_response(self, user: User) -> UserAuthResponse:
        access_payload = {
            "sub": str(user.id),
            "username": user.username,
            "role_id": user.role_id,
            "department_id": user.department_id
        }
        access_token = self.token_service.generate_token(payload=access_payload, expires=timedelta(hours=1))

        jti = str(uuid.uuid4())
        refresh_payload = {
            "sub": str(user.id),
            "jti": jti,
            "type": "refresh"
        }
        refresh_token = self.token_service.generate_token(payload=refresh_payload, expires=timedelta(days=7))

        refresh_token_record = RefreshToken(user_id=user.id, jti=jti, expires_at=refresh_token.expires)
        self.database.add(refresh_token_record)
        self.database.commit()

        return UserAuthResponse(
            username=user.username,
            email=user.email,
            access_token=access_token.token,
            refresh_token=refresh_token.token
        )

    def authenticate_user(self, username: str, password: str) -> UserAuthResponse:
        statement = select(User).where(User.username == username).options(
            selectinload(User.role),
            selectinload(User.department),
        ).limit(1)

        user = self.database.exec(statement).first()
        if not user:
            raise UserNotFoundError("User not found")

        if not self.password_service.check_password(password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect password")

        return self._create_auth_response(user)

    def register_user_and_login(self, user_data: UserCreateSchema) -> UserAuthResponse:
        existing_user = self.database.exec(
            select(User).where(User.username == user_data.username)
        ).first()

        if existing_user:
            raise UsernameAlreadyExistsError("Username already registered")

        hashed_pwd = self.password_service.hash_password(user_data.password)

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pwd,
            role_id=user_data.role_id,
            department_id=user_data.department_id,
            is_active=True
        )

        self.database.add(new_user)
        self.database.commit()
        self.database.refresh(new_user)

        return self._create_auth_response(new_user)

    def refresh_auth_token(self, refresh_token: str) -> UserAuthResponse:
        try:
            payload = self.token_service.decode_jwt(refresh_token)
        except Exception:
            raise InvalidTokenError("Refresh token invalid or expired")

        jti = payload.get("jti")
        user_id = payload.get("sub")

        statement = select(RefreshToken).where(RefreshToken.jti == jti)
        db_token = self.database.exec(statement).first()

        if not db_token:
            raise TokenRevokedError("Token already used or unrecognized")

        user = self.database.get(User, user_id)
        if not user:
            raise UserNotFoundError("User no longer exists")

        self.database.delete(db_token)
        self.database.commit()

        return self._create_auth_response(user)


def get_auth_service(database: Session = Depends(db_connection),
                     password_service: PasswordService = Depends(get_password_service),
                     token_service: TokenService = Depends(get_token_service)) -> AuthService:
    return AuthService(database, password_service, token_service)
