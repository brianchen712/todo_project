from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    username = db.Column(db.Unicode(50))
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

class RegisterLog(db.Model):
    __tablename__ = 'RegisterLog'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100))
    username = db.Column(db.Unicode(50))
    email = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20))  # success / fail
    reason = db.Column(db.Unicode(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoginLog(db.Model):
    __tablename__ = 'LoginLog'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20))  # success / fail
    reason = db.Column(db.Unicode(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Todo(db.Model):
    __tablename__ = 'Todos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    title = db.Column(db.Unicode(128), nullable=False)
    description = db.Column(db.UnicodeText, nullable=False)
    priority = db.Column(db.Unicode(10), nullable=False)
    note = db.Column(db.UnicodeText)
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    repeat = db.Column(db.Unicode(50))
    attachment_filename = db.Column(db.Unicode(255))
    is_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref=db.backref('todos', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "note": self.note,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "repeat": self.repeat,
            "is_done": self.is_done,
            "attachment_filename": self.attachment_filename,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
