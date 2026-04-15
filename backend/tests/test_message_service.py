from uuid import uuid4
from unittest.mock import MagicMock
import pytest
from services.message_service import MessageService
from models import Message

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def message_service(mock_session):
    return MessageService(database=mock_session)

def test_create_message(message_service, mock_session):
    message = Message(role="user", content="Hello", chat_id=uuid4())
    result = message_service.create(message)
    
    assert result.content == "Hello"
    mock_session.add.assert_called_once_with(message)
    mock_session.commit.assert_called_once()

def test_get_all_by_chat_id(message_service, mock_session):
    chat_id = uuid4()
    user_id = 1
    mock_chat = MagicMock()
    mock_chat.id = chat_id
    mock_chat.user_id = user_id
    
    # First call for chat verification
    mock_session.exec.return_value.first.return_value = mock_chat
    
    mock_messages = [
        Message(role="user", content="First", chat_id=chat_id),
        Message(role="ai", content="Second", chat_id=chat_id)
    ]
    # Second call for messages
    mock_session.exec.return_value.all.return_value = mock_messages
    
    result = message_service.get_all_by_chat_id(chat_id, user_id=user_id, limit=5, offset=0)
    
    assert len(result) == 2
    assert result[0].content == "Second"
    assert result[1].content == "First"

def test_get_one_message(message_service, mock_session):
    mock_message = Message(id=1, role="user", content="Test", chat_id=uuid4())
    mock_session.exec.return_value.first.return_value = mock_message
    
    result = message_service.get_one(1)
    
    assert result.id == 1
    assert result.content == "Test"

def test_delete_message(message_service, mock_session):
    mock_message = Message(id=1, role="user", content="Delete me", chat_id=uuid4())
    mock_session.exec.return_value.first.return_value = mock_message
    
    result = message_service.delete(1)
    
    assert result.id == 1
    mock_session.delete.assert_called_once_with(mock_message)
    mock_session.commit.assert_called_once()
