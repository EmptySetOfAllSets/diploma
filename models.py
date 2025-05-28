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
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=True)

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    avaliable = db.Column(db.Boolean, nullable=False)
    ingredients = db.relationship('Ingredient', backref='dish', lazy=True)
    positions = db.relationship('Position', backref='dish', lazy=True)
    dish_type_id = db.Column(db.Integer, db.ForeignKey('dish_type.id'), nullable=False)
    cascade='save-update, merge, delete'

class Dish_type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, unique=True)
    dishes = db.relationship('Dish', backref='dish_type', lazy=True)  # Исправлено groc на dishes

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(300), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Integer, primary_key=False, default = 1)
    # ingredients = db.relationship('Ingredient', backref='dish', lazy=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    cascade='save-update, merge, delete'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Дата и время создания
    delivery_time = db.Column(db.DateTime, nullable=True)  # Планируемое время доставки
    
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=True)
    order_status_id = db.Column(db.Integer, db.ForeignKey('order_status.id'), nullable=False)
    
    positions = db.relationship('Position', 
                              backref='order', 
                              cascade='all, delete-orphan',
                              lazy='dynamic')

class Order_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, index=True)
    orders = db.relationship('Order', backref='status', lazy=True)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, index=True)
    phone = db.Column(db.String(300), nullable=False, index=True)
    orders = db.relationship('Order', backref='client', lazy=True)
    
    def can_be_deleted(self):
        return len(self.orders) == 0

class Delivery (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False, index=True)
    adress = db.Column(db.String(300), nullable=False, index=True)
    orders = db.relationship('Order', backref='delivery', lazy=True)
    delivery_status_id = db.Column(db.Integer, db.ForeignKey('delivery_status.id'), nullable=True)

class Delivery_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, index=True)
    deliveries = db.relationship('Delivery', backref='status', lazy=True)
