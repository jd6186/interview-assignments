from fastapi import FastAPI, APIRouter, Depends, Security, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from common.db_setup import get_db
from common.entity import User, UserUpdateLog, UserDeleteLog
from common.security import verify_token, security, get_password_hash
from common.dto.base_response_dto import ResponseDto
from common.error_types import ErrorType
from common.dto.user_dto import CreateUserDTO, UpdateUserDTO


app = FastAPI(
    title="User Service API",
    description="이용자 백엔드 서비스",
    version="1.0.0"
)
router = APIRouter(prefix="/users")

@router.get("/", description="User 목록 불러오기 API")
def get_users(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    verify_token(credentials)
    users = [item.to_dict() for item in db.query(User).offset(offset).limit(limit).all()]
    total_count = db.query(User).count()
    return ResponseDto.success_response(data=users, total_count=total_count)

# 유저 상세정보 조회 API
@router.get("/{user_login_email}", description="User 상세정보 불러오기 API")
def get_user(user_login_email: str, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    verify_token(credentials)
    user = db.query(User).filter(User.login_email == user_login_email).first()
    if not user:
        return ResponseDto.error_response(ErrorType.USER_NOT_FOUND)
    return ResponseDto.success_response(data=user.to_dict())

@router.post("/", description="User 생성 API")
def create_user(user: CreateUserDTO, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    user_id = verify_token(credentials)

    # 사용자 중복 확인
    existing_user = db.query(User).filter(User.login_email == user.login_email).first()
    if existing_user:
        return ResponseDto.error_response(ErrorType.BAD_REQUEST)

    new_user = User(**user.dict())
    hashed_password = get_password_hash(new_user.password)
    new_user.password = hashed_password
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return ResponseDto.success_response(data=new_user.to_dict())

@router.put("/", description="User 정보 수정 API")
def update_user(user: UpdateUserDTO, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    user_id = verify_token(credentials)
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        return ResponseDto.error_response(ErrorType.USER_NOT_FOUND)

    # 변경 사항 기록
    changes = []
    for key, value in user.dict().items():
        if getattr(existing_user, key) != value:
            changes.append(f"{key}: {getattr(existing_user, key)} -> {value}")
            setattr(existing_user, key, value)
    if changes:
        db.add(UserUpdateLog(user_id=user_id, updated_by=user_id, changes=", ".join(changes)))
    db.commit()
    db.refresh(existing_user)
    return ResponseDto.success_response(data=existing_user.to_dict())

@router.delete("/", description="User 삭제 API")
def delete_user(reason: str, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    user_id = verify_token(credentials)
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        return ResponseDto.error_response(ErrorType.USER_NOT_FOUND)
    # 삭제 이력 추가
    db.add(UserDeleteLog(user_id=user_id, login_email=existing_user.login_email, reason=reason))
    # 사용자 삭제
    db.delete(existing_user)
    db.commit()
    return ResponseDto.success_response(data={"reason": reason})

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
