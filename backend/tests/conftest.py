import os
import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path to resolve imports when running from the 'tests' directory
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# Mocking modules that might cause issues during collection if they try to connect to something
# Or setting environment variables before imports happen

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["QDRANT_HOST"] = "localhost"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("QDRANT_HOST", "localhost")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
