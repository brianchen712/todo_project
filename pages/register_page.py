
from selenium.webdriver.common.by import By
from .base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait

class RegisterPage(BasePage):
    PATH = "/register"

    ACCOUNT = (By.ID, "account")
    PASSWORD = (By.ID, "reg_password")
    USERNAME = (By.ID, "username")
    EMAIL = (By.ID, "email")
    BTN_SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    def open(self):
        super().open(self.PATH)

    def register(self, account, password, username, email):
        self.wait(*self.ACCOUNT)
        self.find(*self.ACCOUNT).send_keys(account or "")
        self.find(*self.PASSWORD).send_keys(password or "")
        self.find(*self.USERNAME).send_keys(username or "")
        self.find(*self.EMAIL).send_keys(email or "")
        self.find(*self.BTN_SUBMIT).click()

    def is_success(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: "/login" in d.current_url
            )
            return True
        except:
            return False

    def get_error_messages(self):
        return [e.text for e in self.driver.find_elements(By.CSS_SELECTOR, "p.error")]

    def has_error_message(self, text):
        return text in self.get_error_messages()