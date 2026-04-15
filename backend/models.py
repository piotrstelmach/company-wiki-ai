from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship


class UploadedFiles(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    file_path: str
    status: str = "processed"
    chunk_count: int
    upload_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Chat(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    messages: List["Message"] = Relationship(back_populates="chat", cascade_delete=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Optional["User"] = Relationship(back_populates="chats")


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    role: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    chat_id: UUID = Field(foreign_key="chat.id")
    chat: Chat = Relationship(back_populates="messages")


class UserRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None

    users: List["User"] = Relationship(back_populates="role")


class Department(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    code: Optional[str] = Field(default=None, unique=True)


class JobTitle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)  # np. "DevOps Engineer"
    department_id: int = Field(foreign_key="department.id")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=255, nullable=False)
    hashed_password: str = Field(nullable=False)
    email: str = Field(nullable=False)
    role_id: int = Field(foreign_key="userrole.id")
    is_active: bool = True
    chats: List[Chat] = Relationship(back_populates="user")
    department_id: Optional[int] = Field(default=None, foreign_key="department.id")
    job_title_id: Optional[int] = Field(default=None, foreign_key="jobtitle.id")

    role: UserRole = Relationship(back_populates="users")
    department: Optional[Department] = Relationship()
    job_title: Optional[JobTitle] = Relationship()

class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    jti: str = Field(index=True, unique=True)
    user_id: int = Field(foreign_key="user.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
