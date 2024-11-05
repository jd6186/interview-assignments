from pydantic import BaseModel


class RegisterRequest(BaseModel):
    login_email: str
    password: str
    name: str
    gender: str
    age: int
    phone: str


class LoginRequest(BaseModel):
    login_email: str
    password: str