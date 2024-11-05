from fastapi import FastAPI, APIRouter, Depends, Security, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from common.db_setup import get_db
from common.entity import Post
from common.security import verify_token, security
from common.dto.base_response_dto import ResponseDto
from common.error_types import ErrorType
from datetime import datetime

from common.dto.post_dto import PostDTO

app = FastAPI(
    title="Post Service API",
    description="게시판 백엔드 서비스",
    version="1.0.0"
)
router = APIRouter(prefix="/posts")

@router.get("/", description="게시판 목록 불러오기 API")
def get_posts(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    verify_token(credentials)
    posts = [item.to_dict() for item in db.query(Post).offset(offset).limit(limit).all()]
    return ResponseDto.success_response(data=posts)

@router.get("/{post_id}", description="선택된 게시판 글 확인 API")
def get_post(post_id: int, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    verify_token(credentials)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return ResponseDto.error_response(ErrorType.USER_NOT_FOUND)
    return ResponseDto.success_response(data=post.to_dict())

@router.post("/", description="게시판 글 작성 API")
def create_post(post: PostDTO, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    user_id = verify_token(credentials)
    new_post = Post(**post.dict(), user_id=user_id, updated_at=datetime.utcnow())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return ResponseDto.success_response(data=new_post.to_dict())

@router.put("/{post_id}", description="게시판 글 수정 API")
def update_post(post_id: int, post: PostDTO, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    user_id = verify_token(credentials)
    existing_post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    if not existing_post:
        return ResponseDto.error_response(ErrorType.USER_NOT_FOUND)

    for key, value in post.dict().items():
        setattr(existing_post, key, value)
    existing_post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(existing_post)
    data = existing_post.to_dict()
    return ResponseDto.success_response(data=data)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
