from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: int
    department_id: int

class UserLoginResponse(BaseModel):
    username: str
    email: str
    access_token: str

class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class UserRegisterResponse(BaseModel):
    username: str
    email: str
    token: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserAuthResponse(BaseModel):
    username: str
    email: str
    access_token: str
    refresh_token: str