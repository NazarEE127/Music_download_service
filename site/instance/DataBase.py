from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    ava = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    downloads = db.Column(db.Integer, default=0)
    albums = db.Column(db.Integer, default=0)
    recommendations = db.Column(db.Integer, default=0)
