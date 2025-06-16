from selenium.webdriver.common.by import By
from .base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait

class TodoPage(BasePage):
    BTN_CREATE = (By.CSS_SELECTOR, "button.btn-green[onclick*='/todo/create']")
    FIELD_TITLE = (By.ID, "title")
    FIELD_DESCRIPTION = (By.ID, "description")
    SELECT_PRIORITY = (By.ID, "priority")
    TAB_SCHEDULE = (By.CSS_SELECTOR, '.tab[data-tab="advanced"]')
    FIELD_START_DATE = (By.ID, "start_date")
    FIELD_END_DATE = (By.ID, "end_date")
    SELECT_REPEAT = (By.ID, "repeat")
    FIELD_NOTE = (By.ID, "note")
    FIELD_ATTACHMENT = (By.ID, "attachment")
    BTN_SAVE = (By.CSS_SELECTOR, "button[type='submit']")
    LIST_ITEMS = (By.CSS_SELECTOR, "#todo-list tbody tr")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".message-success")
    BTN_EDIT_FIRST = (By.CSS_SELECTOR, "#todo-list tbody tr:first-child a[href*='/edit']")
    BTN_DELETE_FIRST = (By.CSS_SELECTOR, "#todo-list tbody tr:first-child a[href*='/delete']")
    BTN_TOGGLE_DONE_FIRST = (By.CSS_SELECTOR, "#todo-list tbody tr:first-child button.btn-status-toggle")
    STATUS_FIRST = (By.CSS_SELECTOR, "#todo-list tbody tr:first-child td:nth-child(4)")
    CHECKBOXES = (By.CSS_SELECTOR, ".select-item")
    BTN_BATCH_DELETE = (By.CSS_SELECTOR, "button.btn-batch-delete")
    BTN_VIEW_FIRST = (By.CSS_SELECTOR, "#todo-list tbody tr:first-child a[href*='/view']")

    def click_view_first(self):
        self.wait(*self.BTN_VIEW_FIRST)
        self.find(*self.BTN_VIEW_FIRST).click()

    def click_create(self):
        print("[DEBUG] current_url (before click):", self.driver.current_url)
        self.wait(*self.BTN_CREATE)  # 確保按鈕存在
        self.find(*self.BTN_CREATE).click()
        print("[DEBUG] current_url (after click):", self.driver.current_url)
        WebDriverWait(self.driver, 5).until(
            lambda d: "/todo/create" in d.current_url
        )

        # 額外等待 modal 或表單 render 完成
        self.wait(*self.FIELD_TITLE)

    def fill_form_and_submit(self, **kwargs):
        self.wait(*self.FIELD_TITLE)
        self.find(*self.FIELD_TITLE).clear()
        self.find(*self.FIELD_TITLE).send_keys(kwargs["title"])
        self.find(*self.FIELD_DESCRIPTION).clear()
        self.find(*self.FIELD_DESCRIPTION).send_keys(kwargs["description"])
        self.select_option(self.SELECT_PRIORITY, kwargs["priority"])
        self.find(*self.FIELD_NOTE).clear()
        self.find(*self.FIELD_NOTE).send_keys(kwargs["note"])
        if "attachment" in kwargs and kwargs["attachment"]:
            self.find(*self.FIELD_ATTACHMENT).send_keys(kwargs["attachment"])

        self.find(*self.TAB_SCHEDULE).click()
        self.wait(*self.FIELD_START_DATE)
        self.set_input_value(self.FIELD_START_DATE, kwargs["start_date"])
        self.set_input_value(self.FIELD_END_DATE, kwargs["end_date"])
        self.find(*self.BTN_SAVE).click()

    def count_todos(self):
        return len(self.finds(*self.LIST_ITEMS))

    def has_success_message(self):
        self.wait(*self.SUCCESS_MESSAGE)
        return self.find(*self.SUCCESS_MESSAGE).is_displayed()

    def click_edit_first(self):
        self.wait(*self.BTN_EDIT_FIRST)
        self.find(*self.BTN_EDIT_FIRST).click()

    def click_delete_first(self):
        self.wait(*self.BTN_DELETE_FIRST)
        self.find(*self.BTN_DELETE_FIRST).click()
        self.handle_alert()

    def get_all_titles(self):
        self.wait(*self.LIST_ITEMS)
        items = self.finds(*self.LIST_ITEMS)
        return [item.find_element(By.TAG_NAME, "strong").text for item in items]

    def toggle_done_first(self):
        self.wait(*self.BTN_TOGGLE_DONE_FIRST)
        self.find(*self.BTN_TOGGLE_DONE_FIRST).click()

    def get_first_status_text(self):
        self.wait(*self.STATUS_FIRST)
        return self.find(*self.STATUS_FIRST).text

    def wait_status_change(self, old_text, timeout=5):
        WebDriverWait(self.driver, timeout).until(
            lambda d: self.find(*self.STATUS_FIRST).text != old_text
        )
        return self.find(*self.STATUS_FIRST).text

    def delete_all_todos(self):
        while True:
            items = self.finds(*self.LIST_ITEMS)
            if not items:
                break
            try:
                # 只針對最上面那一筆進行刪除
                delete_link = items[0].find_element(By.CSS_SELECTOR, "a[href*='/delete']")
                delete_link.click()
                self.handle_alert()
            except Exception as e:
                print(f"[WARN] 刪除項目失敗：{e}")
                break

    def get_all_checkboxes(self):
        return self.finds(*self.CHECKBOXES)

    def select_checkboxes_by_indexes(self, indexes):
        checkboxes = self.get_all_checkboxes()
        for i in indexes:
            if i < len(checkboxes):
                self.driver.execute_script("arguments[0].scrollIntoView(true);", checkboxes[i])
                if not checkboxes[i].is_selected():
                    checkboxes[i].click()

    def click_batch_delete_button(self):
        self.find(*self.BTN_BATCH_DELETE).click()