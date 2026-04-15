from typing import List, Annotated, Optional
from uuid import UUID

from fastapi import Depends
from sqlmodel import select, Session

from database import db_connection
from models import Chat
from services.rest_service import IRestService


class ChatService(IRestService):
    def __init__(self, database: Session = Depends(db_connection)):
        self.database = database

    def create(self, chat: Chat) -> Chat:
        self.database.add(chat)
        self.database.commit()
        self.database.refresh(chat)
        return chat

    def get_all(self, limit: int = 10, offset: int = 0, user_id: Optional[int] = None) -> List[Chat]:
        statement = select(Chat)
        if user_id is not None:
            statement = statement.where(Chat.user_id == user_id)
        get_all_statement = statement.offset(offset).limit(limit)
        chats = self.database.exec(get_all_statement).all()

        return list(chats)

    def get_one(self, entity_id: UUID, user_id: Optional[int] = None) -> Chat:
        find_statement = select(Chat).where(Chat.id == entity_id)
        if user_id is not None:
            find_statement = find_statement.where(Chat.user_id == user_id)
        founded_chat = self.database.exec(find_statement).first()

        if founded_chat is None:
            raise Exception("Chat not found")
        else:
            return founded_chat

    def update(self, entity_id: UUID, chat_data: dict, user_id: Optional[int] = None) -> Chat:
        db_chat = self.get_one(entity_id, user_id=user_id)
        for key, value in chat_data.items():
            setattr(db_chat, key, value)
        self.database.add(db_chat)
        self.database.commit()
        self.database.refresh(db_chat)
        return db_chat

    def delete(self, entity_id: UUID, user_id: Optional[int] = None) -> Chat:
        find_statement = select(Chat).where(Chat.id == entity_id)
        if user_id is not None:
            find_statement = find_statement.where(Chat.user_id == user_id)
        founded_chat = self.database.exec(find_statement).first()
        if founded_chat is None:
            raise Exception("Chat not found")
        else:
            self.database.delete(founded_chat)
            self.database.commit()
            return founded_chat


def get_chat_service(database: Session = Depends(db_connection)) -> IRestService:
    return ChatService(database)


ChatServiceDep = Annotated[IRestService, Depends(get_chat_service)]
