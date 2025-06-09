import pytest, os
from datetime import datetime, timedelta
from pages.login_page import LoginPage
from pages.todo_page import TodoPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models import db, Todo
from utils import get_user_by_account, count_todos_by_user, get_todo_by_userid_and_title

pytestmark = pytest.mark.order(4)
@pytest.mark.todo
def test_create_edit_delete_todo(driver, app_context):
    # 登入
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")
    driver.save_screenshot("screenshots/step1_login_success.png")


    user = get_user_by_account(account="test")
    todo = TodoPage(driver)
    before_count = count_todos_by_user(user.id)
    todo.click_create()
    driver.save_screenshot("screenshots/step5_create_form.png")

    # 新增
    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    todo.fill_form_and_submit(
        title="自動化任務 A",
        description="新增任務說明",
        priority="高",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每天",
        note="初始備註"
    )
    assert todo.has_success_message()
    driver.save_screenshot("screenshots/step6_todo_list_after_create.png")
    #刷新session保證數據準確
    db.session.expire_all()
    after_create_count = count_todos_by_user(user.id)
    assert after_create_count == before_count + 1

    # 編輯
    todo.click_edit_first()
    todo.fill_form_and_submit(
        title="自動化任務 A 已編輯",
        description="更新說明",
        priority="中",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每周",
        note="已編輯備註"
    )
    assert todo.has_success_message()
    driver.save_screenshot("screenshots/step6_edit_done.png")
    db.session.expire_all()
    after_edit_count = count_todos_by_user(user.id)
    assert after_edit_count == after_create_count

    # 刪除
    todo.click_delete_first()
    assert todo.has_success_message()
    driver.save_screenshot("screenshots/step6_after_delete.png")
    db.session.expire_all()
    after_delete_count = count_todos_by_user(user.id)
    assert after_delete_count == before_count

    login.click_logout_button()

@pytest.mark.todo
@pytest.mark.parametrize("account, password", [
    ("test", "P@ssw0rd_X9g2#"),
    ("user_new", "U$erN3w!Qz7^")
])
def test_todo_crud_by_multiple_users(driver, account, password, app_context):
    login = LoginPage(driver)
    login.open()
    login.login(account, password)

    user = get_user_by_account(account=account)
    todo = TodoPage(driver)
    before_count = count_todos_by_user(user.id)
    todo.click_create()

    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    todo.fill_form_and_submit(
        title=f"{account} 任務",
        description="描述 for 多帳號",
        priority="中",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每天",
        note="測試資料"
    )
    assert todo.has_success_message()
    # 刷新session保證數據準確
    db.session.expire_all()
    after_create = count_todos_by_user(user.id)
    assert after_create == before_count + 1

    todo.click_edit_first()
    todo.fill_form_and_submit(
        title=f"{account} 任務已編輯",
        description="已編輯描述",
        priority="低",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每周",
        note="已編輯備註"
    )
    assert todo.has_success_message()
    db.session.expire_all()
    after_edit = count_todos_by_user(user_id=user.id)
    assert after_edit == after_create

    todo.click_delete_first()
    db.session.expire_all()
    after_delete = count_todos_by_user(user_id=user.id)
    assert after_delete == before_count

    login.click_logout_button()

@pytest.mark.todo
@pytest.mark.parametrize("account,password,create_count,delete_count", [
    ("test", "P@ssw0rd_X9g2#", 4, 2),
    ("user_new", "U$erN3w!Qz7^", 2, 1)
])
def test_todo_crud_customized(driver, account, password, create_count, delete_count, app_context):
    login = LoginPage(driver)
    login.open()
    login.login(account, password)

    user = get_user_by_account(account=account)
    todo = TodoPage(driver)
    before_count = count_todos_by_user(user_id=user.id)

    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    # 新增多筆待辦
    for i in range(create_count):
        todo.click_create()
        todo.fill_form_and_submit(
            title=f"{account} 任務 {i+1}",
            description=f"{account} 描述 {i+1}",
            priority="中",
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
            repeat="每天",
            note=f"{account} 備註 {i+1}"
        )
        assert todo.has_success_message()

    db.session.expire_all()
    after_create = count_todos_by_user(user_id=user.id)
    assert after_create == before_count + create_count

    # 刪除部分任務
    for _ in range(delete_count):
        todo.click_delete_first()
        assert todo.has_success_message()

    db.session.expire_all()
    after_delete = count_todos_by_user(user_id=user.id)
    assert after_delete == before_count + (create_count - delete_count)

    login.click_logout_button()

# 增強版：驗證標題是否出現在清單中或刪除後消失
@pytest.mark.todo
def test_create_edit_delete_todo_with_title_check(driver):
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")

    todo = TodoPage(driver)
    todo.click_create()

    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    # 建立待辦
    title = "自動化任務 A"
    todo.fill_form_and_submit(
        title=title,
        description="說明 A",
        priority="高",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每天",
        note="初始備註"
    )
    assert title in todo.get_all_titles()

    # 編輯
    edited_title = "自動化任務 A 已編輯"
    todo.click_edit_first()
    todo.fill_form_and_submit(
        title=edited_title,
        description="更新說明",
        priority="中",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每周",
        note="已編輯備註"
    )
    assert edited_title in todo.get_all_titles()

    # 刪除
    todo.click_delete_first()
    assert edited_title not in todo.get_all_titles()

    login.click_logout_button()

login_cases = [
    {"account": "test", "password": "P@ssw0rd_X9g2#"},
    {"account": "user_new", "password": "U$erN3w!Qz7^"}
]
@pytest.mark.todo
@pytest.mark.parametrize("account, password", [(login_case["account"], login_case["password"]) for login_case in login_cases])
def test_todo_crud_by_multiple_users_with_title_check(driver, account, password):
    login = LoginPage(driver)
    login.open()
    login.login(account, password)

    todo = TodoPage(driver)
    todo.click_create()

    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    title = f"{account} 任務"
    todo.fill_form_and_submit(
        title=title,
        description="描述 for 多帳號",
        priority="中",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每天",
        note="測試資料"
    )
    assert title in todo.get_all_titles()

    # 編輯
    edited_title = f"{account} 任務已編輯"
    todo.click_edit_first()
    todo.fill_form_and_submit(
        title=edited_title,
        description="已編輯描述",
        priority="低",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每周",
        note="已編輯備註"
    )
    assert edited_title in todo.get_all_titles()

    # 刪除
    todo.click_delete_first()
    assert edited_title not in todo.get_all_titles()

    login.click_logout_button()

@pytest.mark.todo
@pytest.mark.parametrize("account,password,create_count,delete_count", [
    ("test", "P@ssw0rd_X9g2#", 4, 2),
    ("user_new", "U$erN3w!Qz7^", 2, 1)
])
def test_todo_crud_customized_with_title_check(driver, account, password, create_count, delete_count):
    login = LoginPage(driver)
    login.open()
    login.login(account, password)

    todo = TodoPage(driver)

    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    titles = []
    for i in range(create_count):
        title = f"{account} 任務 {i+1}"
        titles.append(title)
        todo.click_create()
        todo.fill_form_and_submit(
            title=title,
            description=f"{account} 描述 {i+1}",
            priority="中",
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
            repeat="每天",
            note=f"{account} 備註 {i+1}"
        )
        assert todo.has_success_message()
        assert title in todo.get_all_titles()

    for _ in range(delete_count):
        todo.click_delete_first()
        assert todo.has_success_message()

    remaining_titles = todo.get_all_titles()
    expected_remaining = titles[:-delete_count]
    for title in expected_remaining:
        assert title in remaining_titles

    login.click_logout_button()

@pytest.mark.todo
def test_create_todo_missing_required_fields(driver):
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")

    todo = TodoPage(driver)
    todo.click_create()

    # 留空標題
    todo.fill_form_and_submit(
        title="",
        description="描述A",
        priority="高",
        start_date="2025-06-02",
        end_date="2025-06-03",
        repeat="每天",
        note="備註A"
    )
    assert "todo/list" not in driver.current_url
    login.click_logout_button()

@pytest.mark.todo
def test_create_todo_invalid_date_format(driver):
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")

    todo = TodoPage(driver)
    todo.click_create()

    # 錯誤的日期格式（或空值）
    todo.fill_form_and_submit(
        title="標題B",
        description="描述B",
        priority="中",
        start_date="06-02-2025",  # 用 "06-02-2025"
        end_date="2025-06-03",
        repeat="每天",
        note="備註B"
    )
    assert "todo/list" not in driver.current_url
    login.click_logout_button()

@pytest.mark.todo
def test_create_todo_with_attachment_without_note(driver, app_context):
    # 登入
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")

    user = get_user_by_account(account="test")
    todo = TodoPage(driver)
    before_count =  count_todos_by_user(user_id=user.id)
    todo.click_create()
    driver.save_screenshot("screenshots/step7_upload_file.png")

    # 設定測試檔案路徑
    file_name = "inputDate.png"
    file_path = os.path.abspath(f"tests/files/{file_name}")
    assert os.path.exists(file_path), f"測試檔案不存在：{file_path}"

    # 填寫其他欄位（留空 note）
    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    todo.fill_form_and_submit(
        title="測試上傳但無備註",
        description="這是測試描述",
        priority="高",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每天",
        note="",  # 備註空白
        attachment=file_path
    )

    # 驗證新增成功
    assert todo.has_success_message()
    driver.save_screenshot("screenshots/step7_uploaded_done.png")
    db.session.expire_all()
    after_count = count_todos_by_user(user_id=user.id)
    assert after_count == before_count + 1

    todo.click_view_first()

    db.session.expire_all()
    created = get_todo_by_userid_and_title(user_id=user.id, title="測試上傳但無備註")
    assert created is not None
    assert created.attachment_filename == file_name

    # 驗證檔案名稱是否顯示在頁面（代表成功上傳並顯示）
    assert file_name in driver.page_source
    driver.save_screenshot("screenshots/step7_verify_attachment_name.png")

    # 登出
    login.click_logout_button()

@pytest.mark.todo
def test_toggle_todo_done_status(driver, app_context):
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")

    user = get_user_by_account(account="test")
    todo = TodoPage(driver)
    todo.click_create()

    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    title = "完成狀態切換測試任務"
    todo.fill_form_and_submit(
        title=title,
        description="描述：測試狀態切換",
        priority="中",
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        repeat="每天",
        note="初始狀態為未完成"
    )
    # 確認狀態為「未完成」
    status_before = todo.get_first_status_text()
    assert "未完成" in status_before
    driver.save_screenshot("screenshots/step8_status_before.png")
    db.session.expire_all()
    created_todo = get_todo_by_userid_and_title(user_id=user.id, title=title)
    assert created_todo and created_todo.is_done == False

    # 切換成「已完成」
    todo.toggle_done_first()
    status_after_done = todo.wait_status_change(status_before)
    driver.save_screenshot("screenshots/step8_toggle_done.png")
    assert "已完成" in status_after_done
    db.session.expire_all()
    updated_todo = db.session.get(Todo, created_todo.id)
    assert updated_todo.is_done == True

    # 再次切換回「未完成」
    todo.toggle_done_first()
    status_after_undo = todo.wait_status_change(status_after_done)
    driver.save_screenshot("screenshots/step8_toggle_undo.png")
    assert "未完成" in status_after_undo
    db.session.expire_all()
    reverted_todo = db.session.get(Todo, created_todo.id)
    assert reverted_todo.is_done == False

    login.click_logout_button()

@pytest.mark.todo
def test_batch_delete_selected_todos(driver, app_context):
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")

    user = get_user_by_account(account="test")
    todo = TodoPage(driver)

    # 建立三筆資料
    today = datetime.today().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=2)

    titles = []
    for i in range(3):
        title = f"這是批次測試 {i+1}"
        titles.append(title)
        todo.click_create()
        todo.fill_form_and_submit(
            title=title,
            description="描述",
            priority="中",
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
            repeat="每天",
            note="備註"
        )
        assert todo.has_success_message()

    db.session.expire_all()
    for title in titles:
        assert get_todo_by_userid_and_title(user_id=user.id, title=title) is not None

    # 勾選第 0 與第 2 筆，點擊批次刪除
    driver.save_screenshot("screenshots/step9_batch_delete_before.png")
    todo.select_checkboxes_by_indexes([0, 2])
    todo.click_batch_delete_button()
    todo.handle_alert()  # confirm alert
    driver.save_screenshot("screenshots/step9_batch_delete_after.png")
    assert todo.has_success_message()

    # 剩下第 2 筆（索引 1）
    remaining = [t for t in todo.get_all_titles() if t.startswith("這是批次測試")]
    assert titles[1] in remaining
    assert titles[0] not in remaining
    assert titles[2] not in remaining

    assert get_todo_by_userid_and_title(user_id=user.id, title=titles[1]) is not None
    assert get_todo_by_userid_and_title(user_id=user.id, title=titles[0]) is None
    assert get_todo_by_userid_and_title(user_id=user.id, title=titles[2]) is None

@pytest.mark.todo
def test_batch_delete_without_selection_shows_alert(driver, app_context):
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")

    user = get_user_by_account(account="test")
    todo = TodoPage(driver)

    # 頁面上至少一筆資料
    db.session.expire_all()
    existing_count = count_todos_by_user(user_id=user.id)
    if existing_count == 0:
        todo.click_create()
        today = datetime.today().date()
        start = today + timedelta(days=1)
        end = today + timedelta(days=2)
        todo.fill_form_and_submit(
            title="測試未勾選批次刪除",
            description="desc",
            priority="高",
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
            repeat="每天",
            note="note"
        )
        assert todo.has_success_message()
        db.session.expire_all()
        assert get_todo_by_userid_and_title(user_id=user.id, title="測試未勾選批次刪除") is not None

    # 不勾選，直接按批次刪除 → 捕捉 alert
    todo.click_batch_delete_button()

    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    assert "請先勾選要刪除的任務" in alert.text
