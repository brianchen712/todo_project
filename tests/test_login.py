import pytest
from pages.login_page import LoginPage
from utils import get_user_by_account

pytestmark = pytest.mark.order(2)
@pytest.mark.login
def test_login_success(driver, app_context):
    login = LoginPage(driver)
    login.open()
    login.login("test", "P@ssw0rd_X9g2#")
    # 驗證頁面跳轉成功
    assert login.is_success("/todo/list")

    # 登出
    login.click_logout_button()

    # 查資料庫
    user = get_user_by_account("test")
    assert user is not None
@pytest.mark.login
def test_login_wrong_password(driver):
    login = LoginPage(driver)
    login.open()
    login.login("test", "wrongpass")
    driver.save_screenshot("screenshots/step2_login_fail.png")
    assert not login.is_success("/todo/list")
    assert login.has_error_message("帳號或密碼錯誤")
@pytest.mark.login
def test_login_nonexistent_account(driver):
    login = LoginPage(driver)
    login.open()
    login.login("nouser", "P@ssw0rd_X9g2#")
    assert not login.is_success("/todo/list")
    assert login.has_error_message("帳號或密碼錯誤")
@pytest.mark.login
def test_login_empty_account(driver):
    login = LoginPage(driver)
    login.open()
    login.login("", "P@ssw0rd_X9g2#")
    assert not login.is_success("/todo/list")
    assert login.has_error_message("帳號為必填")
@pytest.mark.login
def test_login_empty_password(driver):
    login = LoginPage(driver)
    login.open()
    login.login("test", "")
    assert not login.is_success("/todo/list")
    assert login.has_error_message("密碼為必填")
@pytest.mark.login
def test_login_empty_both(driver):
    login = LoginPage(driver)
    login.open()
    login.login("", "")
    assert not login.is_success("/todo/list")
    assert login.has_error_message("帳號為必填")
    assert login.has_error_message("密碼為必填")
@pytest.mark.login
def test_go_to_register_page(driver):
    login = LoginPage(driver)
    login.open()
    login.go_to_register()
    assert login.is_success("/register")