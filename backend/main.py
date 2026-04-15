from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from dto.user import UserLoginResponse, UserLoginRequest, UserCreateSchema
from services.auth_service import AuthService, get_auth_service
from services.security import CurrentUserDep
from services.chat_service import ChatServiceDep
from services.file_service import FileServiceDep
from services.message_service import MessageServiceDep
from services.ai_service import AiServiceDep
from models import Chat, Message
from database import create_db_and_tables
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("create connection")
    create_db_and_tables()
    yield
    print("connection closed")


# Initialize application
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Chat-Id"],
)


@app.get("/")
def read_root():
    return {"message": "Company Wiki AI API is running hehe"}


@app.post("/process_file")
async def process_file(
        background_tasks: BackgroundTasks,
        file_service: FileServiceDep,
        department_id: int,
        file: UploadFile = File(...),
):
    try:
        extra_data = {"department_id": department_id}
        document = file_service.process_file(file, background_tasks, extra_data)
        return {"status": "processing", "db_id": document.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot process document: {e}")


from typing import Optional


class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None


@app.get('/chats')
def get_all_chats(
        chat_service: ChatServiceDep,
        user: CurrentUserDep,
        limit: int = 10,
        offset: int = 0
):
    try:
        chats = chat_service.get_all(user_id=user.id, limit=limit, offset=offset)
        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot fetch chats: {e}")


@app.delete('/chats/{chat_id}')
def delete_chat(
        chat_id: UUID,
        chat_service: ChatServiceDep,
        user: CurrentUserDep
):
    try:
        deleted_chat = chat_service.delete(chat_id, user_id=user.id)
        return deleted_chat
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot delete chat: {e}")


class CreateChatRequest(BaseModel):
    title: Optional[str] = "New conversation"


@app.post('/chats')
def create_chat(
        request: CreateChatRequest,
        chat_service: ChatServiceDep,
        user: CurrentUserDep
):
    new_chat = Chat(title=request.title[:50], user_id=user.id)
    return chat_service.create(new_chat)


@app.get('/chats/{chat_id}/messages')
def get_chat_messages(
        chat_id: UUID,
        message_service: MessageServiceDep,
        user: CurrentUserDep,
        limit: int = 20,
        offset: int = 0
):
    try:
        messages = message_service.get_all_by_chat_id(chat_id, user_id=user.id, limit=limit, offset=offset)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot fetch messages: {e}")


@app.post("/chat")
async def chat(
        request: ChatRequest,
        chat_service: ChatServiceDep,
        message_service: MessageServiceDep,
        ai_service: AiServiceDep,
        user: CurrentUserDep
):
    if request.chat_id:
        chat_id = UUID(request.chat_id)
        try:
            chat_service.get_one(chat_id, user_id=user.id)
        except Exception:
            raise HTTPException(status_code=404, detail="Chat not found")
    else:
        new_chat = Chat(title=request.message[:50], user_id=user.id)
        created_chat = chat_service.create(new_chat)
        chat_id = created_chat.id

    user_message = Message(
        role="user",
        content=request.message,
        chat_id=chat_id
    )
    message_service.create(user_message)

    # Reload chat history to include the message we just added
    chat_history = message_service.get_all_by_chat_id(chat_id, user_id=user.id)
    
    # We want to exclude the last message (the one we just added) from context retrieval 
    # but include it in the prompt if build_prompt expects it.
    # Actually, get_context uses request.message, and build_prompt uses chat_history.
    # If chat_history includes the current user_message, build_prompt will have it.
    
    context = ai_service.get_context(request.message, user.department_id)
    prompt = ai_service.build_prompt(chat_history[:-1], context, request.message)

    async def generate():
        full_text = ""
        async for chunk in ai_service.astream_response(prompt):
            full_text += chunk
            yield f"{chunk}"

        response_message = Message(role="ai", content=full_text, chat_id=chat_id)
        message_service.create(response_message)

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"X-Chat-Id": str(chat_id)}
    )


@app.post("/auth/login")
async def login(request: UserLoginRequest, response: Response, auth_service: AuthService = Depends(get_auth_service)) -> UserLoginResponse:
    try:
        user = auth_service.authenticate_user(request.username, request.password)
        response.set_cookie(key="refresh_token", value=user.refresh_token, httponly=True)
        return UserLoginResponse(username=user.username, email=user.email, access_token=user.access_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/auth/refresh")
async def refresh_token(request: Request, response: Response, auth_service: AuthService = Depends(get_auth_service)) -> UserLoginResponse:
    refresh_token_cookie = request.cookies.get("refresh_token")
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    try:
        user = auth_service.refresh_auth_token(refresh_token_cookie)
        response.set_cookie(key="refresh_token", value=user.refresh_token, httponly=True)
        return UserLoginResponse(username=user.username, email=user.email, access_token=user.access_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/auth/register")
async def register(
    request: UserCreateSchema,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserLoginResponse:
    try:
        user = auth_service.register_user_and_login(request)
        return UserLoginResponse(
            username=user.username,
            email=user.email,
            access_token=user.access_token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
