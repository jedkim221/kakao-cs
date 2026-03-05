from pydantic import BaseModel


class KakaoUser(BaseModel):
    id: str


class KakaoUserRequest(BaseModel):
    user: KakaoUser
    utterance: str


class KakaoRequest(BaseModel):
    userRequest: KakaoUserRequest
