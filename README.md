# 📋 自動化測試專案 - 提醒事項系統

本專案是一個使用 Flask + MSSQL 實作的提醒事項系統，支援會員註冊/登入、提醒事項 CRUD、附件上傳與狀態切換。
搭配 Selenium 與 requests 實作 UI 及 API 層級的自動化測試，並整合 GitHub Actions 執行 CI、自動產出 HTML 與 Allure 測試報告。

已完成[測試計畫書.docx](https://github.com/user-attachments/files/20788802/default.docx)及[測試案例總表.xlsx](https://github.com/user-attachments/files/20788815/default.xlsx)撰寫，並遵照總表內容轉化成程式

---

## 🚀 功能概述

- ✅ **會員功能：支援註冊、登入與登出，整合 JWT 驗證機制以保護使用者資料**
- ✅ **提醒事項管理：提供新增、編輯、刪除、查看等完整 CRUD 操作**
- ✅ **狀態切換功能：可於清單頁即時切換提醒事項完成狀態（未完成 ↔ 已完成）**
- ✅ **檔案附件功能：每筆提醒事項可上傳附件並於頁面顯示連結**
- ✅ **操作紀錄追蹤：自動記錄登入與註冊行為 log，強化安全性與可追溯性**
- ✅ **API 自動化測試：使用 requests + pytest 驗證 API 成功與錯誤處理邏輯**
- ✅ **GitHub Actions 自動測試 + 報告上傳**

---

## 📁 專案結構

```
├── app.py                # 主應用程式
├── config.py             # DB 與上傳設定
├── init_database.py      # 建立 TEST 資料庫（MSSQL）
├── init_data.py          # 建立 TEST 資料庫資料表與預設測試帳號
├── models.py             # User / Todo / Log 資料表定義
├── utils.py              # JWT、欄位驗證、log 紀錄、上傳工具
├── requirements.txt      # 所需套件
├── pytest.ini            # 測試標籤與報告設定

├── templates/            # HTML 樣板（登入、註冊、表單、清單）
├── static/               # CSS、圖檔、附件上傳
├── data/                 # 測試資料（YAML）
├── pages/                # Selenium Page Object 模組
├── tests/                # 測試腳本（UI + API）
│   └── files/            # 附件測試用檔案
├── screenshots/          # 測試失敗截圖或特定案例截圖
├── allure-results/       # 存放Allure 報告原始資料

└── .github/workflows/    # GitHub Actions CI 設定檔
```

---

## ⚙️ 安裝方式（本機）

```bash
# 安裝套件
pip install -r requirements.txt

# 初始化資料庫（需先啟動 MSSQL，帳密與 port 請確認 config.py 設定）
python init_database.py

# 建立資料表與預設測試帳號
python init_data.py

# 啟動 Flask 應用
python app.py
```

啟動後可透過瀏覽器開啟：`http://127.0.0.1:5000`

---

## 🧪 測試執行方式(本機)

```bash
# 執行所有測試並產出 HTML + Allure 報告
pytest --html=report.html --self-contained-html --alluredir=allure-results

# 執行特定標籤測試
pytest -m login
pytest -m register
pytest -m todo
pytest -m api
```

- `report.html`：HTML 測試報告，可直接用瀏覽器打開
- `allure-results/`：Allure 報告原始資料，可使用 `allure serve` 觀看

---

## 🤖 GitHub Actions 自動化流程

CI透過 .github/workflows/test.yml 自動執行以下完整流程：

1. **啟動 MSSQL 服務（Docker）**  
   - 使用官方 MSSQL 容器，設置台灣地區字元排序與連接帳密  
   - 監控服務啟動狀態，確保資料庫準備就緒後再繼續執行後續步驟

2. **安裝 Python 環境與專案依賴套件**  
   - 安裝 Python 3.11 與 `requirements.txt` 中所列套件  
   - 額外安裝 ODBC 驅動與 `sqlcmd` 工具，以支援 MSSQL 操作

3. **啟動 Flask 應用（背景執行）**  
   - 使用 `nohup` 啟動 Flask 應用，並將 log 儲存於 `flask.log`  
   - 確保應用可提供 UI 測試存取

4. **初始化資料庫與預設測試資料**  
   - 執行 `init_database.py` 建立資料表  
   - 執行 `init_data.py` 新增預設測試帳號等初始資料

5. **建立存放測試案例截圖資料夾**  
   - 建立資料夾存放測試案例的截圖

6. **執行測試並產出報告**  
   - 使用 `pytest` 執行 Selenium + requests 的自動化測試  
   - 同時產出：
     - `report.html`（HTML 測試報告）
     - `allure-results/`（Allure 測試資料）

7. **Allure HTML 產生與部署 Pages**
   - 下載 CLI → 轉換 → 使用 peaceiris/actions-gh-pages 發布
   - [📊 查看 Allure 測試報告（GitHub Pages）](https://brianchen712.github.io/todo_project/)

8. **上傳測試成果與資源（Artifacts）**  
   - 上傳測試報告與測試截圖（如有）至 GitHub Actions  
   - 所有測試結果可供下載與後續分析

9. **失敗時輸出 Flask 應用 log（輔助除錯）**  
   - 若測試失敗，自動顯示 `flask.log` 最後內容以供分析 

---

## 🧾 預設測試帳號

| 帳號   | 密碼             | 備註       |
|--------|----------------|------------|
| test   | P@ssw0rd_X9g2# | 系統內建測試帳號 |

--- 


## 🧪 測試截圖
Step1：成功登入後的提醒清單頁：驗證登入成功會自動導向 /todo/list，並顯示個人提醒清單。
![step1_login_success](https://github.com/user-attachments/assets/7579402c-13e5-4fa9-a0d3-cc99b3b68457)

Step2：登入失敗時顯示錯誤訊息：輸入錯誤帳號密碼，畫面顯示「帳號或密碼錯誤」提示訊息。
![step2_login_fail](https://github.com/user-attachments/assets/bfab57ed-6a4a-4b16-93a9-8f7861927d87)

Step3：註冊成功後跳轉登入頁：使用新帳號註冊後，自動跳轉登入頁面，驗證流程正常。
![step3_register_success](https://github.com/user-attachments/assets/3e590f89-aa12-482e-ad95-31ceeeb9463f)

Step4：重複帳號顯示錯誤：當輸入已存在的帳號時，提示「帳號已存在」錯誤訊息。
![step4_register_duplicate](https://github.com/user-attachments/assets/049ad74e-597c-4d38-9016-6773caafbad8)

Step5：填寫新增任務表單：點選清單畫面的「+新增」後，填寫提醒事項表單畫面。
![step5_create_form](https://github.com/user-attachments/assets/983d905c-635e-4e78-a1d2-b69ab57afadc)

Step6：新增後回到清單畫面：新增完成後跳轉清單，驗證任務正確新增並顯示在列表。
![step6_todo_list_after_create](https://github.com/user-attachments/assets/1419e98f-e356-47f1-ad9f-f497768965e1)

Step6：任務編輯完成訊息：編輯任務內容後送出，顯示成功訊息提示已更新。
![step6_edit_done](https://github.com/user-attachments/assets/6a2c4b35-4370-4bb5-a64a-e1f258181d5b)

Step6：任務刪除後的畫面：點選刪除後清單自動更新，驗證任務成功移除。
![step6_after_delete](https://github.com/user-attachments/assets/4afac2eb-8aae-46f4-86ce-1d3943ae9675)

Step7：點擊新增並選擇檔案：顯示點選「+新增」並上傳檔案附件的畫面。
![step7_upload_file](https://github.com/user-attachments/assets/ea5f5754-5770-46f1-85b9-680220a9f752)

Step7：表單送出成功畫面：附件上傳後成功建立任務，跳轉回清單畫面。
![step7_uploaded_done](https://github.com/user-attachments/assets/a434771b-c936-4818-8f54-3225c5db5e12)

Step7：顯示附件檔案名稱：點選查看任務內容，頁面成功顯示已上傳的檔案名稱連結。
![step7_verify_attachment_name](https://github.com/user-attachments/assets/64646b78-40f6-4770-94df-639acc5d3a98)

Step8：狀態切換前為「未完成」：任務建立後預設為未完成狀態，顯示對應標籤。
![step8_status_before](https://github.com/user-attachments/assets/f58500ea-da5c-403f-9caa-5ccdc0a6db1d)

Step8：狀態切換為「已完成」：點擊切換按鈕後，任務狀態即時變為已完成。
![step8_toggle_done](https://github.com/user-attachments/assets/9ac6ab15-a35c-48e7-be40-c5bc61608fbe)

Step8：再次切換為「未完成」：再次點擊切換按鈕，狀態恢復為未完成。
![step8_toggle_undo](https://github.com/user-attachments/assets/69e0fae6-b777-4653-89ff-1b8c0d433c17)

Step9：批次刪除前的清單：顯示已勾選多筆任務，準備執行批次刪除的畫面。
![step9_batch_delete_before](https://github.com/user-attachments/assets/04295bba-5dfc-408f-b9ac-289f2db5b7f6)

Step9：批次刪除後的清單：刪除成功後僅剩未勾選的任務，清單同步更新。
![step9_batch_delete_after](https://github.com/user-attachments/assets/e5544751-0c5e-4c0f-a003-d765dcfa355f)

Step10：API 建立任務成功的 JSON 回應：透過 requests.post 發送 API，成功回傳 status=201 與 {"message": "成功新增待辦", "id": 78}。
```
{
  "id": 78,
  "message": "成功新增待辦"
}
```
---

## 🏁 後續可擴充項目

- [ ] Playwright 改寫 Selenium 測試

---

## 🙋‍♂️ 聯絡與履歷

若對本專案架構或自動化測試流程有興趣，歡迎技術交流或履歷詢問。

---

## 📎  其餘附件
[完整測試作品集說明（Word 版）下載] [todo_test_portfolio.docx](https://github.com/user-attachments/files/20654628/todo_test_portfolio.docx)







