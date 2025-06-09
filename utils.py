from flask import request, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func
from models import Todo, User
from models import db,LoginLog, RegisterLog
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, UTC
import os, jwt

def log_login(account, status, reason=None):
    try:
        ip = request.remote_addr or 'unknown'
        log = LoginLog(account=account, ip_address=ip, status=status, reason=reason)
        db.session.add(log)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"[log_login] Logging failed: {e}")

def log_register(account, username, email, status, reason=None):
    try:
        ip = request.remote_addr or 'unknown'
        log = RegisterLog(account=account, username=username, email=email, ip_address=ip,
                          status=status, reason=reason)
        db.session.add(log)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"[log_register] Logging failed: {e}")

def validate_todo_fields(form):
    from datetime import datetime, date
    errors = []
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    priority = form.get("priority", "").strip()
    start_date = form.get("start_date", "").strip()
    end_date = form.get("end_date", "").strip()
    repeat = form.get("repeat", "").strip()

    if not title:
        errors.append(("標題為必填", 'basic'))
    if not description:
        errors.append(("說明為必填", 'basic'))
    if not priority:
        errors.append(("優先順序為必填", 'basic'))
    if not start_date:
        errors.append(("請填寫開始日期", 'advanced'))
    if not end_date:
        errors.append(("請填寫結束日期", 'advanced'))
    if not repeat:
        errors.append(("請選擇重複設定", 'advanced'))

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start < date.today():
            errors.append(("開始日不可小於今天", 'advanced'))
        if end < start:
            errors.append(("結束日不可小於開始日", 'advanced'))
    except ValueError:
        errors.append(("日期格式錯誤", 'advanced'))

    return errors


def handle_attachment(file_storage, upload_folder):
    if file_storage and file_storage.filename:
        filename = secure_filename(file_storage.filename)
        save_path = os.path.join(upload_folder, filename)
        file_storage.save(save_path)
        return filename
    return None

# requests測試使用

SECRET_KEY = "supersecret"

def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(UTC) + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None

def get_or_404(model, id):
    instance = db.session.get(model, id)
    if instance is None:
        abort(404)
    return instance

def get_todo_by_id_and_title(todo_id, title, return_mode="first"):
    """
    根據 id 與 title 查詢 Todo，return_mode 可為:
    - "first"：回傳第一筆符合的紀錄，找不到則回傳 None
    - "one_or_none"：預期最多一筆，否則拋出錯誤
    """
    stmt = select(Todo).filter_by(id=todo_id, title=title)

    if return_mode == "one_or_none":
        return db.session.execute(stmt).scalar_one_or_none()
    else:
        return db.session.scalars(stmt).first()

def get_todo_by_userid_and_title(user_id, title, return_mode="first"):
    """
    根據 id 與 title 查詢 Todo，return_mode 可為:
    - "first"：回傳第一筆符合的紀錄，找不到則回傳 None
    - "one_or_none"：預期最多一筆，否則拋出錯誤
    """
    stmt = select(Todo).filter_by(user_id=user_id, title=title)

    if return_mode == "one_or_none":
        return db.session.execute(stmt).scalar_one_or_none()
    else:
        return db.session.scalars(stmt).first()

def get_user_by_account(account, return_mode="first"):
    stmt = select(User).filter_by(account=account)
    if return_mode == "one_or_none":
        return db.session.execute(stmt).scalar_one_or_none()
    return db.session.scalars(stmt).first()

def count_todos_by_user(user_id):
    stmt = select(func.count()).select_from(Todo).filter_by(user_id=user_id)
    return db.session.execute(stmt).scalar_one()

def get_user_todos_desc(user_id: int):
    stmt = select(Todo).where(Todo.user_id == user_id).order_by(Todo.created_at.desc())
    return db.session.scalars(stmt).all()
