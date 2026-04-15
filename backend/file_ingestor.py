import os
import uuid

from langchain_community.embeddings import OllamaEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlmodel import Session, select
from models import UploadedFiles
from database import engine


class FileIngestor:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        )
        qdrant_url = os.getenv("QDRANT_HOST", "http://qdrant:6333")
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = "company_wiki"

    def process(self, file_id: int, location: str, extra_data: dict):
        with Session(engine) as db:
            try:
                collections = self.client.get_collections().collections
                exists = any(c.name == self.collection_name for c in collections)
                if not exists:
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=rest.VectorParams(size=768, distance=rest.Distance.COSINE)
                    )
                loader = PyPDFLoader(location)
                pages = loader.load()
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
                chunks = splitter.split_documents(pages)

                points = []
                for i, chunk in enumerate(chunks):
                    vector = self.embeddings.embed_query(chunk.page_content)
                    point_id = str(uuid.uuid4())

                    points.append(rest.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "text": chunk.page_content,
                            "postgres_id": file_id,
                            "chunk_index": i,
                            "metadata": chunk.metadata,
                            **extra_data
                        }
                    ))

                self.client.upsert(collection_name=self.collection_name, points=points)

                statement = select(UploadedFiles).where(UploadedFiles.id == file_id)
                document_info = db.exec(statement).first()
                if document_info:
                    document_info.status = "processed"
                    document_info.chunk_count = len(chunks)
                    db.add(document_info)
                    db.commit()

            except Exception as e:
                print(f"Ingest error: {e}")
