#!/bin/bash

# 실행중인 Docker Compose 중지
docker-compose down

# 테스트 환경 설정
export TESTING=true

# Docker Compose로 테스트 DB 및 운영 DB 실행
docker-compose up -d db test_db

# 테이블 생성 SQL 명령어
SQL_COMMAND="
DROP TABLE IF EXISTS user_delete_logs;
DROP TABLE IF EXISTS user_update_logs;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    login_email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(50),
    age INTEGER,
    phone VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS user_update_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    updated_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    changes TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS user_delete_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    login_email VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMP DEFAULT NOW(),
    reason TEXT
);
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"

# 운영 DB 컨테이너에 테이블 생성
docker exec -i db psql -U user -d appdb -c "$SQL_COMMAND"

# 테스트 DB 컨테이너에 테이블 생성
docker exec -i test_db psql -U testuser -d testdb -c "$SQL_COMMAND"

# 테스트 실행
echo "Running tests..."
pytest --disable-warnings

# 테스트 결과 확인
if [ $? -eq 0 ]; then
  echo "All tests passed successfully. Starting Docker Compose for application..."
  # 테스트 성공 시 테스트 환경 변수 변경
  export TESTING=false
  # Docker Compose 빌드 및 실행
  docker-compose up -d auth_service user_service post_service
else
  echo "Some tests failed. Please fix the issues before deploying."
  # 테스트 실패 시 Docker Compose 중지
  docker-compose down
  exit 1
fi
