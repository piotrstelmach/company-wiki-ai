import os
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from qdrant_client import QdrantClient

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

llm_model = OllamaLLM(model="llama3.2:3b", base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"))
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
)

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_HOST", "http://qdrant:6333"),
    prefer_grpc=False
)

def get_llm_model():
    return llm_model

def get_embeddings():
    return embeddings

def get_qdrant_client():
    return qdrant_client