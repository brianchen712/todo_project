import pytest
from pages.register_page import RegisterPage
from utils import get_user_by_account

pytestmark = pytest.mark.order(1)
@pytest.mark.register
def test_register_success(driver, app_context):
    register = RegisterPage(driver)
    register.open()
    register.register("user_new", "U$erN3w!Qz7^", "新用戶", "user_new@gmail.com")
    # UI 驗證：是否跳轉成功
    assert register.is_success()
    driver.save_screenshot("screenshots/step3_register_success.png")

    # 資料庫驗證
    user = get_user_by_account(account="user_new")
    assert user is not None
    assert user.username == "新用戶"
    assert user.email == "user_new@gmail.com"

@pytest.mark.register
def test_register_empty_account(driver):
    register = RegisterPage(driver)
    register.open()
    register.register("", "U$erN3w!Qz7^", "用戶A", "a@gmail.com")
    assert not register.is_success()
    assert register.has_error_message("帳號為必填")


@pytest.mark.register
def test_register_empty_password(driver):
    register = RegisterPage(driver)
    register.open()
    register.register("userA", "", "用戶A", "a@gmail.com")
    assert not register.is_success()
    assert register.has_error_message("密碼為必填")


@pytest.mark.register
def test_register_invalid_email(driver):
    register = RegisterPage(driver)
    register.open()
    register.register("userB", "U$erN3w!Qz7^", "用戶B", "not-an-email")
    assert not register.is_success()
    assert register.has_error_message("Email 格式錯誤")


@pytest.mark.register
def test_register_duplicate_account(driver):
    register = RegisterPage(driver)
    register.open()
    # 帳號 user 已存在
    register.register("user_new", "U$erN3w!Qz7^", "新用戶", "user_new@gmail.com")
    driver.save_screenshot("screenshots/step4_register_duplicate.png")
    assert not register.is_success()
    assert register.has_error_message("帳號已存在")