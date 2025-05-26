# models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(162))  # Увеличиваем длину для хеша

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    



class Groc_type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, unique=True)
    groc = db.relationship('Groc', backref='groc_type', lazy=True)

class Groc_unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(50), nullable=False, unique=True)
    groc = db.relationship('Groc', backref='groc_unit', lazy=True)

class Groc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    groc_type_id = db.Column(db.Integer, db.ForeignKey('groc_type.id'), nullable=False)
    groc_unit_id = db.Column(db.Integer, db.ForeignKey('groc_unit.id'), nullable=False)
    ingredients = db.relationship('Ingredient', backref='groc', lazy=True)  # Исправлено на ingredients

class Ingredient(db.Model):  # Исправлено название с Ingridient
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    kkal = db.Column(db.Float, nullable=False)  # Изменено на Float
    description = db.Column(db.String(150))
    groc_id = db.Column(db.Integer, db.ForeignKey('groc.id'), nullable=False)  # Исправлено gorc_id на groc_id
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    ingredients = db.relationship('Ingredient', backref='dish', lazy=True)
    dish_type_id = db.Column(db.Integer, db.ForeignKey('dish_type.id'), nullable=False)

class Dish_type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, unique=True)
    dishes = db.relationship('Dish', backref='dish_type', lazy=True)  # Исправлено groc на dishes