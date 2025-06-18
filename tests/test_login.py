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
@pytest.mark.parametrize("account,password,error_messages,screenshot", [
    ("test", "wrongpass", ["帳號或密碼錯誤"], "screenshots/step2_login_fail.png"),
    ("nouser", "P@ssw0rd_X9g2#", ["帳號或密碼錯誤"], None),
    ("", "P@ssw0rd_X9g2#", ["帳號為必填"], None),
    ("test", "", ["密碼為必填"], None),
    ("", "", ["帳號為必填", "密碼為必填"], None),
])
def test_login_failures(driver, account, password, error_messages, screenshot):
    login = LoginPage(driver)
    login.open()
    login.login(account, password)

    if screenshot:
        driver.save_screenshot(screenshot)

    assert not login.is_success("/todo/list")
    for msg in error_messages:
        assert login.has_error_message(msg)