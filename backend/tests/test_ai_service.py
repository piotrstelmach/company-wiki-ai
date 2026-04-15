from unittest.mock import MagicMock, AsyncMock
import pytest
from services.ai_service import AiService
from models import Message

@pytest.fixture
def mock_llm():
    return MagicMock()

@pytest.fixture
def mock_embeddings():
    return MagicMock()

@pytest.fixture
def mock_qdrant():
    return MagicMock()

@pytest.fixture
def ai_service(mock_llm, mock_embeddings, mock_qdrant):
    return AiService(llm_model=mock_llm, model_embeddings=mock_embeddings, qdrant_client=mock_qdrant)

def test_build_prompt(ai_service):
    history = [
        Message(role="user", content="Hello"),
        Message(role="ai", content="Hi there!")
    ]
    context = "Company policy: No dogs."
    user_message = "Can I bring my dog?"
    
    prompt = ai_service.build_prompt(history, context, user_message)
    
    assert "User: Hello" in prompt
    assert "Assistant: Hi there!" in prompt
    assert "Company policy: No dogs." in prompt
    assert "Can I bring my dog?" in prompt

def test_get_context(ai_service, mock_embeddings, mock_qdrant):
    mock_embeddings.embed_query.return_value = [0.1, 0.2]

    mock_hit = MagicMock()
    mock_hit.payload = {"text": "Dog policy"}
    mock_vector_result = MagicMock()
    mock_vector_result.points = [mock_hit]
    mock_qdrant.query_points.return_value = mock_vector_result

    context = ai_service.get_context("query", user_department_id=1)

    assert "Dog policy" in context
    mock_embeddings.embed_query.assert_called_once_with("query")
    mock_qdrant.query_points.assert_called_once()

@pytest.mark.asyncio
async def test_astream_response(ai_service, mock_llm):
    async def mock_stream(prompt):
        yield "Hello"
        yield " world"
    
    mock_llm.astream.return_value = mock_stream("test")
    
    chunks = []
    async for chunk in ai_service.astream_response("test"):
        chunks.append(chunk)
        
    assert chunks == ["Hello", " world"]
    mock_llm.astream.assert_called_once_with("test")
