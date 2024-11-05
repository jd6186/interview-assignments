import pytest
from fastapi.testclient import TestClient
from auth_service.main import app as auth_app
from user_service.main import app as user_app
from post_service.main import app as post_app

auth_client = TestClient(auth_app)
user_client = TestClient(user_app)
post_client = TestClient(post_app)
register_user_info = {
    "login_email": "testuser@example.com",
    "password": "testpassword",
    "name": "Test User",
    "gender": "Male",
    "age": 30,
    "phone": "123456789"
}
access_token = None  # 전역 변수로 인증 토큰 저장
create_post_id = None  # 정상 생성된 게시글 ID 저장

@pytest.fixture(scope="module")
def register_user():
    response = auth_client.post("/auth/register", json=register_user_info)
    assert response.status_code == 200
    return response

@pytest.fixture(scope="module")
def login_user():
    global access_token
    response = auth_client.post("/auth/login", json={
        "login_email": register_user_info["login_email"],
        "password": register_user_info["password"]
    })
    assert response.status_code == 200
    access_token = response.json()["data"]["access_token"]
    return access_token

def get_auth_headers():
    if access_token:
        return {"Authorization": f"Bearer {access_token}"}
    raise ValueError("Access token is not set. Run the login_user fixture first.")


### 시나리오 1. 유저 등록 후 로그인 시도
# 유저 등록 후 성공적인 회원가입 테스트
def test_register_user_success(register_user):
    assert register_user.json()["success"] == True

# 유저 등록 시 필수 필드 누락 테스트
def test_register_user_missing_fields():
    response = auth_client.post("/auth/register", json={
        "login_email": "newuser@example.com",
        # password 필드 누락
        "name": "New User",
        "gender": "Female",
        "age": 28,
        "phone": "987654321"
    })
    assert response.status_code == 422  # 필수 필드 누락 시 422 응답

# 이미 존재하는 사용자로 회원가입 시도 테스트
def test_register_existing_user():
    response = auth_client.post("/auth/register", json=register_user_info)
    assert response.json()["status_code"] == 400  # 이미 존재하는 사용자에 대해 400 응답
    assert response.json()["success"] == False

# 유저 로그인 성공 테스트
def test_login_user_success(login_user):
    headers = get_auth_headers()
    assert "Authorization" in headers

# 잘못된 자격 증명으로 로그인 시도 테스트
def test_login_invalid_credentials():
    response = auth_client.post("/auth/login", json={
        "login_email": "wronguser@example.com",
        "password": "wrongpassword"
    })
    assert response.json()["status_code"] == 401
    assert response.json()["success"] == False

# 만료된 토큰으로 요청 시도
def test_access_with_invalid_token():
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    response = post_client.get("/posts", headers=invalid_headers)
    assert response.status_code == 401  # 만료되거나 잘못된 토큰으로 접근 시 401 응답


### 시나리오 2. 게시글 CRUD 테스트
# 게시글 생성 성공 테스트
def test_create_post():
    global create_post_id
    headers = get_auth_headers()
    response = post_client.post("/posts", json={
        "title": "Test Post",
        "content": "This is a test post"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] == True
    create_post_id = response.json()["data"]["id"]  # 생성된 post_id 저장

# 게시글 목록 조회 성공 테스트
def test_get_posts():
    headers = get_auth_headers()
    response = post_client.get("/posts", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

# 특정 게시글 조회 성공 테스트
def test_get_specific_post():
    headers = get_auth_headers()
    response = post_client.get(f"/posts/{create_post_id}", headers=headers)  # 저장된 post_id 사용
    assert response.status_code == 200
    assert response.json()["success"] == True

# 잘못된 post_id로 특정 게시물 조회 테스트
def test_get_invalid_post():
    headers = get_auth_headers()
    response = post_client.get("/posts/9999", headers=headers)  # 존재하지 않는 post_id
    assert response.json()["status_code"] == 404  # 존재하지 않는 리소스에 대해 404 응답
    assert response.json()["success"] == False

# 게시글 수정 성공 테스트
def test_update_post():
    headers = get_auth_headers()
    response = post_client.put(f"/posts/{create_post_id}", json={  # 저장된 post_id 사용
        "title": "Updated Test Post",
        "content": "Updated content"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] == True

# 잘못된 post_id로 게시글 업데이트 테스트
def test_update_invalid_post():
    headers = get_auth_headers()
    response = post_client.put("/posts/9999", json={
        "title": "Updated Test Post",
        "content": "Updated content"
    }, headers=headers)
    assert response.json()["status_code"] == 404  # 존재하지 않는 리소스에 대해 404 응답
    assert response.json()["success"] == False


### 시나리오 3. 유저 CRUD 테스트
# 유저 생성 성공 테스트
def test_create_user():
    headers = get_auth_headers()
    response = user_client.post("/users", json={
        "login_email": "newuser@example.com",
        "password": "newpassword",
        "name": "New User",
        "gender": "Female",
        "age": 28,
        "phone": "987654321"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] == True

# 유저 정보 업데이트 성공 테스트
def test_update_user():
    headers = get_auth_headers()
    response = user_client.put("/users", json={
        "name": "Updated User",
        "gender": "Female",
        "age": 35,
        "phone": "111111111"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] == True

# 유저 삭제 성공 테스트
def test_delete_user():
    headers = get_auth_headers()
    response = user_client.delete(f"/users?reason=Test deletion", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] == True

# 존재하지 않는 사용자 업데이트 시도
def test_update_nonexistent_user():
    headers = get_auth_headers()
    response = user_client.put("/users", json={
        "name": "Nonexistent User",
        "gender": "Female",
        "age": 35,
        "phone": "123456789"
    }, headers=headers)
    assert response.json()["status_code"] == 404  # 존재하지 않는 사용자에 대해 404 응답
    assert response.json()["success"] == False

# 삭제 후 GET /users로 삭제된 유저 조회 시도
def test_get_deleted_user():
    headers = get_auth_headers()
    response = user_client.get(f"/users/{register_user_info['login_email']}", headers=headers)  # 저장된 user_id 사용
    print(response.json())
    assert response.json()["status_code"] == 404  # 존재하지 않는 리소스에 대해 404 응답
    assert response.json()["success"] == False
