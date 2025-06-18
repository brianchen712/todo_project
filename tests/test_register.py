import pytest
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from utils import get_user_by_account

pytestmark = pytest.mark.order(1)
@pytest.mark.register
def test_register_with_all_fields(driver, app_context):
    login = LoginPage(driver)
    login.open()
    login.go_to_register()

    register = RegisterPage(driver)
    register.register("user_new", "U$erN3w!Qz7^", "新用戶", "user_new@gmail.com")

    # UI 驗證
    assert register.is_success()
    driver.save_screenshot("screenshots/step3_register_full_info.png")

    # DB 驗證
    user = get_user_by_account("user_new")
    assert user is not None

@pytest.mark.register
def test_register_with_required_fields_only(driver, app_context):
    login = LoginPage(driver)
    login.open()
    login.go_to_register()

    register = RegisterPage(driver)
    register.register("brian", "U$erN3w!Qz7^", "", "")

    # UI 驗證
    assert register.is_success()
    driver.save_screenshot("screenshots/step3_register_required_only.png")

    # DB 驗證
    user = get_user_by_account("brian")
    assert user is not None

@pytest.mark.register
@pytest.mark.parametrize("account,password,username,email,expected_error", [
    ("", "U$erN3w!Qz7^", "用戶A", "a@gmail.com", "帳號為必填"),
    ("userA", "", "用戶A", "a@gmail.com", "密碼為必填"),
    ("userB", "U$erN3w!Qz7^", "用戶B", "not-an-email", "Email 格式錯誤"),
    ("user_new", "U$erN3w!Qz7^", "新用戶", "user_new@gmail.com", "帳號已存在"),
])
def test_register_failed_cases(driver, account, password, username, email, expected_error):
    login = LoginPage(driver)
    login.open()
    login.go_to_register()

    register = RegisterPage(driver)
    register.register(account, password, username, email)

    assert not register.is_success()
    assert register.has_error_message(expected_error)

    if expected_error == "帳號已存在":
        driver.save_screenshot("screenshots/step4_register_duplicate.png")