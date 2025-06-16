from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

class BasePage:
    """
    Page Object 基底類別：
    - 提供通用的 `open`, `find`, `wait` 等方法
    - child page 只需定義 URL path 及元件操作
    """
    def __init__(self, driver, base_url="http://127.0.0.1:5000"):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def delay(self, seconds=0.7):
        time.sleep(seconds)

    # ---------- 通用操作 ----------
    def open(self, path: str):
        self.delay()  # 每次 find 前都延遲 0.5 秒
        self.driver.get(f"{self.base_url}{path}")

    def find(self, by, selector):
        self.delay()  # 每次 find 前都延遲 0.5 秒
        return self.driver.find_element(by, selector)

    def finds(self, by, selector):
        self.delay()  # 每次 finds 前都延遲
        return self.driver.find_elements(by, selector)

    def select_option(self, locator, text):
        """根據 locator 與顯示文字選擇下拉選單選項"""
        element = self.find(*locator)
        select = Select(element)
        select.select_by_visible_text(text)

    def wait(self, by, selector, timeout=5):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )

    def handle_alert(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            print(f"[DEBUG] Alert text: {alert.text}")
            alert.accept()

            # 等待 alert 被處理完，不然下一行操作會報錯
            WebDriverWait(self.driver, timeout).until_not(EC.alert_is_present())
            return True
        except:
            return False

    def set_input_value(self, locator, value):
        """使用 JavaScript 設定 input 元件的值（穩定、不觸發 UI 問題）"""
        element = self.find(*locator)
        self.driver.execute_script("arguments[0].value = arguments[1]", element, value)

    # 取得所有錯誤訊息文字
    def get_error_messages(self):
        return [e.text for e in self.driver.find_elements(By.CSS_SELECTOR, "p.error")]
    # texts = []
    # for e in self.driver.find_elements(By.CSS_SELECTOR, "p.error"):
    #   texts.append(e.text)
    # return texts

    def has_error_message(self, text):
        return text in self.get_error_messages()
