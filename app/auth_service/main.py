from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.orm import Session

from common.dto.auth_dto import RegisterRequest, LoginRequest
from common.db_setup import get_db
from common.security import create_access_token, verify_password, get_password_hash
from common.entity import User
from common.dto.base_response_dto import ResponseDto
from common.error_types import ErrorType

app = FastAPI(
    title="Auth Service API",
    description="회원가입 및 로그인을 위한 백엔드 서비스",
    version="1.0.0"
)
router = APIRouter(prefix="/auth")

@router.post("/register", description="회원가입 API")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    # 사용자 중복 확인
    existing_user = db.query(User).filter(User.login_email == user.login_email).first()
    if existing_user:
        return ResponseDto.error_response(ErrorType.BAD_REQUEST)

    # 새로운 사용자 추가
    hashed_password = get_password_hash(user.password)
    new_user = User(
        login_email=user.login_email,
        password=hashed_password,
        name=user.name,
        gender=user.gender,
        age=user.age,
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return ResponseDto.success_response(data=new_user.to_dict())

@router.post("/login", description="로그인 API")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.login_email == user.login_email).first()
    print(existing_user)
    if not existing_user or not verify_password(user.password, existing_user.password):
        return ResponseDto.error_response(ErrorType.INVALID_CREDENTIALS)

    # 토큰 생성 시 user ID 사용
    token = create_access_token(existing_user.id)
    return ResponseDto.success_response(data={"access_token": token})


app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
