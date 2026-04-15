from typing import List, Annotated

from fastapi import Depends
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

from dependencies import get_llm_model, get_embeddings, get_qdrant_client
from models import Message


class AiService:
    def __init__(
            self,
            llm_model: Ollama = Depends(get_llm_model),
            model_embeddings: OllamaEmbeddings = Depends(get_embeddings),
            qdrant_client: QdrantClient = Depends(get_qdrant_client),
    ):
        self.llm_model = llm_model
        self.model_embeddings = model_embeddings
        self.qdrant_client = qdrant_client

    def get_context(self, query: str, user_department_id: int, limit: int = 3) -> str:
        query_vector = self.model_embeddings.embed_query(query)

        rbac_filter = Filter(
            should=[
                FieldCondition(
                    key="department_id",
                    match=MatchValue(value=user_department_id)
                ),
                FieldCondition(
                    key="department_id",
                    match=MatchValue(value=-1)
                )
            ]
        )

        vector_result = self.qdrant_client.query_points(
            collection_name="company_wiki",
            query=query_vector,
            query_filter=rbac_filter,
            limit=limit,
            with_payload=True
        )

        context = ""
        for hit in vector_result.points:
            text = hit.payload.get("text", "No content")
            context += f"\n---\n{text}\n"

        print("\n" + "="*50)
        print(f"DEBUG: user department_id = {user_department_id}")
        print(f"DEBUG: FOUND CONTEXT:\n{context}")
        print("="*50 + "\n")

        return context

    def build_prompt(self, history: List[Message], context: str, user_message: str) -> str:
        history_lines = []
        for msg in history:
            prefix = "User" if msg.role == "user" else "Assistant"
            history_lines.append(f"{prefix}: {msg.content}")

        chat_history_str = "\n".join(history_lines)

        # PROMPT ALIGNED TO THE LEFT EDGE
        prompt = f"""You are an internal, professional company assistant. Your ONLY task is to answer questions based on the provided CONTEXT below.

<context>
{context}
</context>

<chat_history>
{chat_history_str}
</chat_history>

ABSOLUTE RULES:
1. Answer strictly based on the facts contained in the <context> section.
2. If the <context> section is empty or does not contain the answer to the question, YOU ARE FORBIDDEN from using your own knowledge. You must answer with exactly this sentence: "I do not have information on this topic in the available documents."
3. Answer in English. Be concise and specific.

USER QUESTION: {user_message}

YOUR ANSWER:"""
        return prompt

    async def astream_response(self, prompt: str):
        async for chunk in self.llm_model.astream(prompt):
            yield chunk


def get_ai_service(
        llm_model: Ollama = Depends(get_llm_model),
        model_embeddings: OllamaEmbeddings = Depends(get_embeddings),
        qdrant_client: QdrantClient = Depends(get_qdrant_client),
) -> AiService:
    return AiService(llm_model, model_embeddings, qdrant_client)


AiServiceDep = Annotated[AiService, Depends(get_ai_service)]