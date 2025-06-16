from selenium import webdriver
import time, tempfile, pytest, requests, allure, os, uuid
from app import app

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture
def app_context():
    with app.app_context():
        yield

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")

    # 使用唯一乾淨 user profile 資料夾（避免 session 衝突）
    user_data_dir = tempfile.mkdtemp(prefix=f"profile-{uuid.uuid4()}-")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    # 隱藏自動化控制提示與防止干擾
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")

    # 停用密碼提示與下載彈窗
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    # 禁用「安全性提示」功能
    options.add_argument("--disable-features=PasswordCheck")
    options.add_argument("--disable-features=AutofillServerCommunication")

    # 降低干擾，例如某些網站會攔截自動化行為（防bot）
    options.add_argument("--disable-blink-features=AutomationControlled")

    # ✅ 只有在 CI 環境（如 GitHub Actions）時才啟用無頭模式
    if os.getenv("CI") == "true":
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    yield driver
    time.sleep(1)
    driver.quit()

# Allure: 自動截圖
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            os.makedirs("screenshots", exist_ok=True)
            file_name = f"screenshots/{item.name}.png"
            driver.save_screenshot(file_name)
            with open(file_name, "rb") as image_file:
                allure.attach(image_file.read(), name="screenshot", attachment_type=allure.attachment_type.PNG)

@pytest.fixture
def auth_token():
    res = requests.post(f"{BASE_URL}/api/login", json={
        "account": "test",
        "password": "P@ssw0rd_X9g2#"
    })
    assert res.status_code == 200
    return res.json()["token"]