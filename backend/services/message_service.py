from typing import List, Annotated, Optional
from uuid import UUID

from fastapi import Depends
from sqlmodel import select, Session

from database import db_connection
from models import Message, Chat
from services.rest_service import IRestService


class MessageService(IRestService):
    def __init__(self, database: Session = Depends(db_connection)):
        self.database = database

    def create(self, message: Message) -> Message:
        self.database.add(message)
        self.database.commit()
        self.database.refresh(message)
        return message

    def get_all_by_chat_id(self, chat_id: UUID, user_id: int, limit: int = 5, offset: int = 0) -> List[Message]:
        # Verify chat belongs to user
        chat_statement = select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        chat = self.database.exec(chat_statement).first()
        if not chat:
            raise Exception("Chat not found or access denied")

        statement = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.desc()).offset(offset).limit(limit)
        messages = list(self.database.exec(statement).all())
        messages.reverse()
        return messages

    def get_all(self, limit: int = 100, offset: int = 0, user_id: Optional[int] = None) -> List[Message]:
        statement = select(Message).offset(offset).limit(limit)
        return list(self.database.exec(statement).all())

    def get_one(self, entity_id: int, user_id: Optional[int] = None) -> Message:
        statement = select(Message).where(Message.id == entity_id)
        message = self.database.exec(statement).first()
        if not message:
            raise Exception("Message not found")
        return message

    def update(self, entity_id: int, message_data: dict, user_id: Optional[int] = None) -> Message:
        db_message = self.get_one(entity_id, user_id=user_id)
        for key, value in message_data.items():
            setattr(db_message, key, value)
        self.database.add(db_message)
        self.database.commit()
        self.database.refresh(db_message)
        return db_message

    def delete(self, entity_id: int, user_id: Optional[int] = None) -> Message:
        db_message = self.get_one(entity_id, user_id=user_id)
        self.database.delete(db_message)
        self.database.commit()
        return db_message


def get_message_service(database: Session = Depends(db_connection)) -> MessageService:
    return MessageService(database)


MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]
