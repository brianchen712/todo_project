import pytest, yaml
from pages.login_page import LoginPage
from utils import get_user_by_account

with open("data/login_cases.yml", encoding="utf-8") as f:
    login_cases = yaml.safe_load(f) or []

pytestmark = pytest.mark.order(3)
@pytest.mark.login
@pytest.mark.parametrize("case", login_cases, ids=[case["id"] for case in login_cases])
def test_login_param(driver, case, app_context):
    login = LoginPage(driver)
    login.open()
    login.wait(*LoginPage.ACCOUNT)
    login.login(case["account"], case["password"])
    if case["success"]:
        # 驗證頁面跳轉成功
        assert login.is_success("/todo/list")
        # 登出
        login.click_logout_button()
        # 查資料庫
        user = get_user_by_account(case["account"])
        assert user is not None
    else:
        assert not login.is_success("/todo/list")
        if "expected_error" in case:
            errors = case["expected_error"]
            for msg in errors:
                assert login.has_error_message(msg)