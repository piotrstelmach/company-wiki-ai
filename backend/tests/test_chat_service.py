from uuid import UUID, uuid4
from unittest.mock import MagicMock
import pytest
from services.chat_service import ChatService
from models import Chat

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def chat_service(mock_session):
    return ChatService(database=mock_session)

def test_create_chat(chat_service, mock_session):
    chat = Chat(title="Test Chat")
    result = chat_service.create(chat)
    
    assert result.title == "Test Chat"
    mock_session.add.assert_called_once_with(chat)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(chat)

def test_get_all_chats(chat_service, mock_session):
    mock_chats = [Chat(title="Chat 1"), Chat(title="Chat 2")]
    mock_session.exec.return_value.all.return_value = mock_chats
    
    result = chat_service.get_all(limit=10, offset=0)
    
    assert len(result) == 2
    assert result[0].title == "Chat 1"
    assert result[1].title == "Chat 2"

def test_get_one_chat(chat_service, mock_session):
    chat_id = uuid4()
    mock_chat = Chat(id=chat_id, title="Test Chat")
    mock_session.exec.return_value.first.return_value = mock_chat
    
    result = chat_service.get_one(chat_id)
    
    assert result.id == chat_id
    assert result.title == "Test Chat"

def test_get_one_chat_not_found(chat_service, mock_session):
    mock_session.exec.return_value.first.return_value = None
    
    with pytest.raises(Exception):
        chat_service.get_one(uuid4())

def test_update_chat(chat_service, mock_session):
    chat_id = uuid4()
    mock_chat = Chat(id=chat_id, title="Old Title")
    mock_session.exec.return_value.first.return_value = mock_chat
    
    updated_data = {"title": "New Title"}
    result = chat_service.update(chat_id, updated_data)
    
    assert result.title == "New Title"
    mock_session.add.assert_called_with(mock_chat)
    mock_session.commit.assert_called()

def test_delete_chat(chat_service, mock_session):
    chat_id = uuid4()
    mock_chat = Chat(id=chat_id, title="To Delete")
    mock_session.exec.return_value.first.return_value = mock_chat
    
    result = chat_service.delete(chat_id)
    
    assert result.id == chat_id
    mock_session.delete.assert_called_once_with(mock_chat)
    mock_session.commit.assert_called_once()
