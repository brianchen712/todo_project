# init_data.py
from app import app, db
from models import User

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='測試').first():
        test_user = User(account='test', password='P@ssw0rd_X9g2#', username='測試', email='test@gmail.com')
        test_user.set_password(test_user.password)
        db.session.add(test_user)
        db.session.commit()
        print("✅ 初始化完成：建立 test 使用者")
    else:
        print("ℹ️ test 使用者已存在")