from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))

    def init(self, name, email):
        self.name = name
        self.email = email

class Reports(db.Model):
    __tablename__ = 'reports'

    id = db.Column("id", db.Integer, primary_key=True)
    json_data = db.Column("frames", db.JSON, nullable=False)  # Массив JSON-ов
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Время создания
    username = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)

    def init(self, json_data, username):
        self.json_data = json_data
        self.created_at = datetime.utcnow
        self.username = username
