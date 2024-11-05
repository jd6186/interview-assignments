from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 운영 및 테스트용 데이터베이스 URL 설정
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/appdb")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://testuser:testpassword@localhost:5433/testdb")

# 환경에 따라 데이터베이스 URL 선택
IS_TESTING = os.getenv("TESTING", "false").lower() == "true"
selected_database_url = TEST_DATABASE_URL if IS_TESTING else DATABASE_URL

# 데이터베이스 엔진 생성
engine = create_engine(selected_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 데이터베이스 세션 생성 함수
def get_db():
    """운영 및 테스트 환경에 따라 올바른 데이터베이스 세션을 반환"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
