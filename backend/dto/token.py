from pydantic import BaseModel


class GenerateTokenResponse(BaseModel):
    token: str
    expires: str


