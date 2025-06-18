import requests, pytest, json
from app import app
from unittest.mock import patch
from utils import generate_token, get_todo_by_id_and_title
from models import db, Todo
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:5000"

pytestmark = pytest.mark.order(5)
@pytest.mark.api
def test_create_todo_api_success(auth_token, app_context):
    start = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    end = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
    res = requests.post(f"{BASE_URL}/api/todo",
                        headers={"Authorization": f"Bearer {auth_token}"},
                        json={
                            "title": "測試 API 任務",
                            "description": "自動化測試用",
                            "priority": "高",
                            "start_date": start,
                            "end_date": end,
                            "repeat": "每天"
                        })
    assert res.status_code == 201
    assert "成功新增待辦" in res.json()["message"]
    with open("screenshots/step10_api_create_success.txt", "w", encoding="utf-8") as f:
        json.dump(res.json(), f, ensure_ascii=False, indent=2)

    db.session.expire_all()
    id = res.json()["id"]
    assert get_todo_by_id_and_title(id, "測試 API 任務") is not None

@pytest.mark.api
def test_create_todo_db_fail(auth_token):
    with app.test_client() as client, patch("models.db.session.commit") as mock_commit:
        mock_commit.side_effect = Exception("模擬資料庫錯誤")

        # 模擬 token
        token = generate_token(user_id=1)  # 測試資料庫中必須有 user_id = 1 的使用者

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        start = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        end = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")

        payload = {
            "title": "測試失敗案例",
            "description": "故意觸發",
            "priority": "中",
            "start_date": start,
            "end_date": end,
            "repeat": "每天"
        }

        res = client.post("/api/todo", data=json.dumps(payload), headers=headers)
        assert res.status_code == 500
        assert "內部錯誤" in res.get_json()["error"]

@pytest.mark.api
def test_get_single_todo(auth_token, app_context):
    start = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    end = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
    create_res = requests.post(f"{BASE_URL}/api/todo", headers={"Authorization": f"Bearer {auth_token}"}, json={
        "title": "單筆查詢測試",
        "description": "測試用",
        "priority": "中",
        "start_date": start,
        "end_date": end,
        "repeat": "每天"
    })
    todo_id = create_res.json()["id"]
    res = requests.get(f"{BASE_URL}/api/todo/{todo_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    assert res.json()["title"] == "單筆查詢測試"

    db.session.expire_all()
    assert db.session.get(Todo, todo_id) is not None

@pytest.mark.api
def test_get_all_todos(auth_token):
    res = requests.get(f"{BASE_URL}/api/todos", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

@pytest.mark.api
def test_update_todo_success(auth_token, app_context):
    start = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    end = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
    create = requests.post(f"{BASE_URL}/api/todo", headers={"Authorization": f"Bearer {auth_token}"}, json={
        "title": "更新前",
        "description": "初始內容",
        "priority": "低",
        "start_date": start,
        "end_date": end,
        "repeat": "每天"
    })
    todo_id = create.json()["id"]
    start = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
    end = (date.today() + timedelta(days=4)).strftime("%Y-%m-%d")
    res = requests.put(f"{BASE_URL}/api/todo/{todo_id}", headers={"Authorization": f"Bearer {auth_token}"}, json={
        "title": "更新後",
        "description": "已更新",
        "priority": "高",
        "start_date": start,
        "end_date": end,
        "repeat": "每周"
    })
    assert res.status_code == 200
    assert "更新成功" in res.json()["message"]

    db.session.expire_all()
    updated = db.session.get(Todo, todo_id)
    assert updated.title == "更新後"
    assert updated.priority == "高"

@pytest.mark.api
def test_delete_todo_success(auth_token, app_context):
    start = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
    end = (date.today() + timedelta(days=4)).strftime("%Y-%m-%d")
    create = requests.post(f"{BASE_URL}/api/todo", headers={"Authorization": f"Bearer {auth_token}"}, json={
        "title": "刪除測試",
        "description": "測試用",
        "priority": "中",
        "start_date": start,
        "end_date": end,
        "repeat": "每天"
    })
    todo_id = create.json()["id"]
    res = requests.delete(f"{BASE_URL}/api/todo/{todo_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    assert "刪除成功" in res.json()["message"]

    db.session.expire_all()
    assert db.session.get(Todo, todo_id) is None

@pytest.mark.api
@pytest.mark.parametrize("method,url_suffix", [
    ("put", "api/todo/999999"),
    ("delete", "api/todo/999999")
])
def test_todo_not_found(auth_token, method, url_suffix):
    url = f"{BASE_URL}/{url_suffix}"
    request_func = getattr(requests, method)
    res = request_func(url, headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 404

@pytest.mark.api
@pytest.mark.parametrize("invalid_field,payload,expected_error", [
    ("title", {
        "description": "缺標題",
        "priority": "高",
        "start_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "repeat": "每天"
    }, "標題為必填"),

    ("description", {
        "title": "缺說明",
        "priority": "高",
        "start_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "repeat": "每天"
    }, "說明為必填"),

    ("priority", {
        "title": "缺優先",
        "description": "優先為空",
        "start_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "repeat": "每天"
    }, "優先順序為必填"),

    ("start_date", {
        "title": "缺開始日期",
        "description": "缺開始日期",
        "priority": "高",
        "end_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "repeat": "每天"
    }, "請填寫開始日期"),

    ("end_date", {
        "title": "缺結束日期",
        "description": "缺結束日期",
        "priority": "高",
        "start_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "repeat": "每天"
    }, "請填寫結束日期"),

    ("repeat", {
        "title": "缺重複設定",
        "description": "缺重複設定",
        "priority": "高",
        "start_date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"),
    }, "請選擇重複設定"),

])
def test_create_todo_validation_errors(auth_token, invalid_field, payload, expected_error):
    res = requests.post(f"{BASE_URL}/api/todo", headers={"Authorization": f"Bearer {auth_token}"}, json=payload)
    assert res.status_code == 400
    assert expected_error in str(res.json()["errors"])