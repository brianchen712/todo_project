# config.py
import os

# 依照環境變數讀取資料庫參數（可在本機或 GitHub Actions 設定）
DB_USER = os.environ.get("DB_USER", "tester")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "qwer1234")  # 預設是本機使用者
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "1433")
DB_NAME = os.environ.get("DB_NAME", "TEST")

SQLALCHEMY_DATABASE_URI = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOAD_FOLDER = 'static/uploads'