from typing import Optional
from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    name: str
    gender: str
    age: int
    phone: str
    login_email: str
    password: str  # 사용자 정보를 입력받기 위한 모델


class UpdateUserDTO(BaseModel):
    name: str
    gender: str
    age: int
    phone: str
