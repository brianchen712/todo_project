
from selenium.webdriver.common.by import By
from .base_page import BasePage
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class LoginPage(BasePage):
    PATH = "/login"
    # locators
    ACCOUNT = (By.ID, "account")
    PASSWORD = (By.ID, "password")
    BTN_LOGIN = (By.CLASS_NAME, "btn-login")
    REGISTER_BTN = (By.CSS_SELECTOR, "form[action='/register'] button")
    HEADING = (By.TAG_NAME, "h2")
    BTN_LOGOUT = (By.CSS_SELECTOR, "a.btn-logout")

    def open(self):
        super().open(self.PATH)

    def login(self, account: str, password: str):
        self.wait(*self.ACCOUNT)
        self.find(*self.ACCOUNT).send_keys(account or "")
        self.find(*self.PASSWORD).send_keys(password or "")
        self.find(*self.BTN_LOGIN).click()

    def click_logout_button(self):
        self.wait(*self.BTN_LOGOUT)
        self.find(*self.BTN_LOGOUT).click()

    def go_to_register(self):
        self.find(*self.REGISTER_BTN).click()

    def is_success(self, page="/todo", timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: page in d.current_url
            )
            return True
        except:
            print(f"[!] 頁面未轉跳至 {page}，目前位於 {self.driver.current_url}")
            return False

    # 取得所有錯誤訊息文字
    def get_error_messages(self):
        return [e.text for e in self.driver.find_elements(By.CSS_SELECTOR, "p.error")]

    def has_error_message(self, text):
        return text in self.get_error_messages()
