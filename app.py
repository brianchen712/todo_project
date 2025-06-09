import traceback
import os
import re
import config
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Todo
from sqlalchemy.exc import IntegrityError
from utils import log_login, log_register, validate_todo_fields, handle_attachment, generate_token, decode_token, get_or_404, get_user_by_account

app = Flask(__name__)
app.secret_key = 'secret'
app.config.from_object(config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # 建立目錄
db.init_app(app)

@app.before_request
def require_login():
    protected_paths = ['/todo']
    if any(request.path.startswith(p) for p in protected_paths):
        if 'user_id' not in session and request.endpoint not in ('login', 'register'):
            return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    is_register = False
    if request.method == 'POST':
        account = request.form.get('account').strip()
        password = request.form.get('password').strip()
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        status, reason = 'success', ''
        # 欄位驗證
        if not account:
            flash("帳號為必填")
        if not password:
            flash("密碼為必填")
        if not account or not password:
            status, reason = 'fail', '欄位為空'
            log_register(account, username, email, status, reason)
            return render_template("register.html")
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            status, reason = 'fail', 'Email 格式錯誤'
            flash(reason)
            log_register(account, username, email, status, reason)
            return render_template('register.html')
        elif len(password) < 4:
            status, reason = 'fail', '密碼需大於 4 個字'
            flash(reason)
            log_register(account, username, email, status, reason)
            return render_template('register.html')
        if get_user_by_account(account=account):
            status, reason = 'fail', '帳號已存在'
            flash(reason)
            log_register(account, username, email, status, reason)
            return render_template('register.html')
        try:
            new_user = User(account=account, username=username or None, email=email or None)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            is_register = True
        except IntegrityError:
            traceback.print_exc()
            db.session.rollback()
            status, reason = 'fail', '有異常狀況，無法註冊'
            flash(reason)
        log_register(account, username, email, status, reason)

    if is_register:
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form.get('account').strip()
        password = request.form.get('password').strip()
        # 輸入驗證（對應空值測試）
        if not account:
            flash('帳號為必填')
        if not password:
            flash('密碼為必填')
        if not account or not password:
            log_login(account, 'fail', '欄位為空')
            return render_template('login.html')

        # 查詢帳號（改為只比對帳號，密碼用 hash 驗證）
        user = get_user_by_account(account=account)
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            log_login(account, 'success')
            return redirect(url_for('todo_list', user_id=user.id))
        else:
            flash('帳號或密碼錯誤')
            log_login(account, 'fail', '帳號或密碼錯誤')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/todo/list')
def todo_list():
    user_id = session.get('user_id')
    print("[DEBUG] session info:", session.get("user_id"), session.get("username"))
    todos = Todo.query.filter_by(user_id=user_id).order_by(Todo.created_at.desc()).all()
    return render_template('todo_list.html', todos=todos)


@app.route('/todo/create', methods=['GET', 'POST'])
def todo_create():
    if request.method == 'POST':
        # 欄位取得與驗證
        errors = validate_todo_fields(request.form)
        if errors:
            for msg, tab in errors:
                flash(msg)
            active_tab = errors[-1][1] if errors else 'basic'
            return render_template("todo_form.html", todo=None, active_tab=active_tab)
        todo = Todo(
            user_id=session['user_id'],
            title=request.form['title'],
            description=request.form.get('description'),
            priority=request.form.get('priority'),
            note=request.form.get('note'),
            start_date=request.form.get('start_date'),
            end_date=request.form.get('end_date'),
            repeat=request.form.get('repeat'),
        )
        file = request.files.get('attachment')
        filename = handle_attachment(file, app.config['UPLOAD_FOLDER'])
        if filename:
            todo.attachment_filename = filename

        db.session.add(todo)
        db.session.commit()
        flash('成功新增待辦')
        return redirect(url_for('todo_list'))
    return render_template('todo_form.html', todo=None)


@app.route('/todo/edit/<int:id>', methods=['GET', 'POST'])
def todo_edit(id):
    todo = get_or_404(Todo, id)
    if todo.user_id != session.get('user_id'):
        flash('無權限編輯')
        return redirect(url_for('todo_list'))
    if request.method == 'POST':
        # 欄位取得與驗證
        errors = validate_todo_fields(request.form)
        if errors:
            for msg, tab in errors:
                flash(msg)
            active_tab = errors[-1][1] if errors else 'basic'
            return render_template("todo_form.html", todo=todo, active_tab=active_tab)
        todo.title = request.form['title']
        todo.description = request.form.get('description')
        todo.priority = request.form.get('priority')
        todo.note = request.form.get('note')
        todo.start_date = request.form.get('start_date')
        todo.end_date = request.form.get('end_date')
        todo.repeat = request.form.get('repeat')

        file = request.files.get('attachment')
        filename = handle_attachment(file, app.config['UPLOAD_FOLDER'])
        if filename:
            todo.attachment_filename = filename

        db.session.commit()
        flash('成功更新待辦')
        return redirect(url_for('todo_list'))
    return render_template('todo_form.html', todo=todo)


@app.route('/todo/delete/<int:id>')
def todo_delete(id):
    todo = get_or_404(Todo, id)
    if todo.user_id != session.get('user_id'):
        flash('無權限刪除')
        return redirect(url_for('todo_list'))
    db.session.delete(todo)
    db.session.commit()
    flash('成功刪除待辦')
    return redirect(url_for('todo_list'))

@app.route('/todo/toggle_done/<int:id>', methods=['POST'])
def todo_toggle_done(id):
    todo = get_or_404(Todo, id)
    if todo.user_id != session.get('user_id'):
        flash('無權限修改')
        return redirect(url_for('todo_list'))

    todo.is_done = not todo.is_done  # 切換 True/False 狀態
    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return '', 204
    return redirect(url_for('todo_list'))

@app.route('/todo/view/<int:id>')
def todo_view(id):
    todo = get_or_404(Todo, id)
    if todo.user_id != session.get('user_id'):
        flash("無權限查看")
        return redirect(url_for('todo_list'))
    return render_template("todo_form.html", todo=todo, readonly=True)

@app.route("/todo/batch-delete", methods=["POST"])
def todo_batch_delete():
    ids = request.form.getlist("selected_ids")
    for todo_id in ids:
        todo = db.session.get(Todo, todo_id)
        if todo and todo.user_id == session.get("user_id"):
            db.session.delete(todo)
    db.session.commit()
    flash("選取的任務已刪除", "success")
    return redirect(url_for("todo_list"))

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = get_user_by_account(account=data.get('account'))
    if user and user.check_password(data.get('password')):
        token = generate_token(user.id)
        return {"token": token}
    return {"error": "登入失敗"}, 401

@app.route('/api/todo', methods=['POST'])
def api_create_todo():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return {"error": "未授權或 token 失效"}, 401

    data = request.json
    errors = validate_todo_fields(data)
    if errors:
        return {"errors": errors}, 400

    try:
        todo = Todo(
            user_id=payload["user_id"],
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            note=data.get('note'),
            start_date=data['start_date'],
            end_date=data['end_date'],
            repeat=data['repeat']
        )
        db.session.add(todo)
        db.session.commit()
        return {"message": "成功新增待辦", "id": todo.id}, 201
    except Exception as e:
        return {"error": "內部錯誤", "detail": str(e)}, 500

@app.route('/api/todos', methods=['GET'])
def api_get_all_todos():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return {"error": "未授權或 token 失效"}, 401

    todos = Todo.query.filter_by(user_id=payload["user_id"]).order_by(Todo.created_at.desc()).all()
    return [todo.to_dict() for todo in todos], 200

@app.route('/api/todo/<int:id>', methods=['GET'])
def api_get_single_todo(id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return {"error": "未授權"}, 401

    todo = get_or_404(Todo, id)
    if todo.user_id != payload["user_id"]:
        return {"error": "無權限"}, 403

    return todo.to_dict(), 200


@app.route('/api/todo/<int:id>', methods=['PUT'])
def api_update_todo(id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return {"error": "未授權"}, 401

    todo = get_or_404(Todo, id)
    if todo.user_id != payload["user_id"]:
        return {"error": "無權限"}, 403

    data = request.json
    todo.title = data.get("title")
    todo.description = data.get("description")
    todo.priority = data.get("priority")
    todo.note = data.get("note")
    todo.start_date = data.get("start_date")
    todo.end_date = data.get("end_date")
    todo.repeat = data.get("repeat")
    db.session.commit()
    return {"message": "更新成功"}, 200

@app.route('/api/todo/<int:id>', methods=['DELETE'])
def api_delete_todo(id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return {"error": "未授權"}, 401

    todo = get_or_404(Todo, id)
    if todo.user_id != payload["user_id"]:
        return {"error": "無權限"}, 403

    db.session.delete(todo)
    db.session.commit()
    return {"message": "刪除成功"}, 200

if __name__ == '__main__':
    app.run(debug=True)