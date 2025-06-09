import pyodbc
import os
import socket

# 判斷是否在 GitHub Actions 環境（或 Ubuntu）
is_ci = os.environ.get("GITHUB_ACTIONS") == "true" or "ubuntu" in socket.gethostname().lower()

# 連線用 sa
DB_HOST = "127.0.0.1"
DB_PORT = "1433"
DB_USER = "sa"
DB_PWD = "YourStrong!Passw0rd"

TARGET_DB_NAME = "TEST"
TARGET_LOGIN = "tester"

# ✅ 根據環境決定密碼
TARGET_PASSWORD = "Qwer1234!" if is_ci else "qwer1234"

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={DB_HOST},{DB_PORT};"
    f"UID={DB_USER};"
    f"PWD={DB_PWD};"
    f"DATABASE=master"
)

try:
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()

    # 建立 login（如果不存在）
    cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sys.sql_logins WHERE name = '{TARGET_LOGIN}')
        BEGIN
            CREATE LOGIN {TARGET_LOGIN} WITH PASSWORD = '{TARGET_PASSWORD}';
        END
    """)

    # 建立資料庫（如果不存在）
    cursor.execute(f"""
        IF DB_ID('{TARGET_DB_NAME}') IS NULL
        BEGIN
            CREATE DATABASE [{TARGET_DB_NAME}];
        END
    """)
    print(f"✅ 資料庫 '{TARGET_DB_NAME}' 確認存在或已建立完成")

    # 設定 login 對應的使用者與權限
    cursor.execute(f"""
        USE [{TARGET_DB_NAME}];
        IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = '{TARGET_LOGIN}')
        BEGIN
            CREATE USER {TARGET_LOGIN} FOR LOGIN {TARGET_LOGIN};
            EXEC sp_addrolemember 'db_owner', '{TARGET_LOGIN}';
        END
    """)
    print(f"✅ Login '{TARGET_LOGIN}' 與資料庫權限設定完成")

except Exception as e:
    print("❌ 資料庫初始化失敗:", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()