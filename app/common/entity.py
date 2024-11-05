from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# 기존 사용자 엔티티
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login_email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    gender = Column(String)
    age = Column(Integer)
    phone = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "login_email": self.login_email,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "phone": self.phone
        }


# 유저 수정 이력 엔티티
class UserUpdateLog(Base):
    __tablename__ = "user_update_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    changes = Column(String, nullable=False)  # 수정된 내용 기록

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "updated_by": self.updated_by,
            "updated_at": self.updated_at,
            "changes": self.changes
        }


# 유저 삭제 이력 엔티티
class UserDeleteLog(Base):
    __tablename__ = "user_delete_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    deleted_by = Column(String, nullable=False)
    deleted_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(String, nullable=True)  # 삭제 사유 기록

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "deleted_by": self.deleted_by,
            "deleted_at": self.deleted_at,
            "reason": self.reason
        }


# 게시글 엔티티
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "updated_at": self.updated_at
        }
