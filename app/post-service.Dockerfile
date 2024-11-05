FROM python:3.9-slim

# 의존성 파일 복사
COPY ./post_service .
COPY ./common ./common

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 서비스 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]