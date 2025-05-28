from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, NumberRange, Length, Regexp, Optional
from models import Groc_type, Groc_unit, Dish_type, Groc, Dish, Ingredient, Client, Order, Order_status, Delivery, Delivery_status
import re
from datetime import datetime

class ProductTypeForm(FlaskForm):
    type = StringField('Тип продукта', validators=[DataRequired()])

class UnitForm(FlaskForm):
    unit = StringField('Единица измерения', validators=[DataRequired()])


# class DishForm(FlaskForm):
#     name = StringField('Название блюда', validators=[DataRequired()])
#     price = FloatField('Цена', validators=[DataRequired(), NumberRange(min=0)])
#     dish_type_id = SelectField('Тип блюда', coerce=int, validators=[DataRequired()])
    
#     def __init__(self, *args, **kwargs):
#         super(DishForm, self).__init__(*args, **kwargs)
#         self.dish_type_id.choices = [(dt.id, dt.type) for dt in Dish_type.query.order_by(Dish_type.type).all()]

class DishForm(FlaskForm):
    name = StringField('Название блюда', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired(), NumberRange(min=0)])
    avaliable = BooleanField('Актуально (отображать в меню)')
    dish_type_id = SelectField('Тип блюда', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(DishForm, self).__init__(*args, **kwargs)
        self.dish_type_id.choices = [(dt.id, dt.type) for dt in Dish_type.query.order_by(Dish_type.type).all()]

class ProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    type_id = SelectField('Тип продукта', coerce=int, validators=[DataRequired()])
    unit_id = SelectField('Единица измерения', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        # Всегда обновляем choices при инициализации формы
        self.type_id.choices = [
            (t.id, t.type) for t in Groc_type.query.order_by(Groc_type.type).all()
        ]
        self.unit_id.choices = [
            (u.id, u.unit) for u in Groc_unit.query.order_by(Groc_unit.unit).all()
        ]
        
        # Явная установка данных для SelectField при редактировании
        if hasattr(self, '_obj'):
            obj = self._obj
            self.type_id.data = obj.groc_type_id
            self.unit_id.data = obj.groc_unit_id


class DishTypeForm(FlaskForm):
    type = StringField('Тип блюда', validators=[DataRequired()])


class IngredientForm(FlaskForm):
    dish_id = SelectField('Блюдо', coerce=int, validators=[DataRequired()])
    groc_id = SelectField('Продукт', coerce=int, validators=[DataRequired()])
    amount = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('Описание', validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(IngredientForm, self).__init__(*args, **kwargs)
        self.dish_id.choices = [(d.id, d.name) for d in Dish.query.order_by(Dish.name).all()]
        self.groc_id.choices = [(g.id, f"{g.name} ({g.groc_type.type})") for g in Groc.query.join(Groc.groc_type).order_by(Groc.name).all()]

class IngredientFormForDish(FlaskForm):
    search = StringField('Поиск продукта')
    product = SelectField('Продукт', coerce=int, validators=[DataRequired()])
    amount = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=1)])
    kkal = FloatField('Калории', validators=[DataRequired(), NumberRange(min=0)])
    def __init__(self, *args, **kwargs):
        super(IngredientForm, self).__init__(*args, **kwargs)
        self._update_product_choices()
    
    def _update_product_choices(self, search_term=None):
        query = Groc.query.join(Groc.groc_unit)
        if search_term:
            query = query.filter(Groc.name.ilike(f'%{search_term}%'))
        self.product.choices = [(g.id, f"{g.name} ({g.groc_unit.unit})") 
                              for g in query.order_by(Groc.name).all()]
    
    def __init__(self, *args, **kwargs):
        super(IngredientFormForDish, self).__init__(*args, **kwargs)
        self.product.choices = [(g.id, f"{g.name} ({g.groc_unit.unit})") 
                              for g in Groc.query.join(Groc.groc_unit).order_by(Groc.name).all()]
    
class ClientForm(FlaskForm):
    name = StringField('Имя клиента', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Имя должно быть от 2 до 100 символов')
    ])
    phone = StringField('Телефон', validators=[
        DataRequired(),
        Length(min=5, max=20, message='Некорректный формат телефона'),
        Regexp(r'^[\d\+\(\)\-\s]+$', message='Только цифры и символы +()-')
    ])

class OrderStatusForm(FlaskForm):
    name = StringField('Тип продукта', validators=[DataRequired()])

class DeliveryStatusForm(FlaskForm):
    name = StringField('Тип продукта', validators=[DataRequired()])

class OrderForm(FlaskForm):
    name = StringField('Название заказа', validators=[
        DataRequired(),
        Length(min=2, max=300)
    ])
    price = FloatField('Сумма', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    created_at = DateTimeField('Дата и время создания', 
                             format='%Y-%m-%d %H:%M',
                             default=datetime.utcnow)
    delivery_time = DateTimeField('Планируемое время доставки',
                                format='%Y-%m-%d %H:%M',
                                validators=[Optional()])
    client_id = SelectField('Клиент', coerce=int, validators=[DataRequired()])
    delivery_id = SelectField('Доставка', coerce=int)
    order_status_id = SelectField('Статус заказа', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.client_id.choices = [(c.id, f"{c.name} ({c.phone})") for c in Client.query.all()]
        self.delivery_id.choices = [(d.id, d.description) for d in Delivery.query.all()]
        self.order_status_id.choices = [(s.id, s.name) for s in Order_status.query.all()]

class PositionForm(FlaskForm):
    dish_id = SelectField('Блюдо', coerce=int, validators=[DataRequired()])
    price = FloatField('Цена', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])

class DeliveryForm(FlaskForm):
    description = StringField('Описание', validators=[DataRequired()])
    adress = StringField('Адрес', validators=[DataRequired()])
    delivery_status_id = SelectField('Статус доставки', coerce=int)

class OrderStatusForm(FlaskForm):
    name = StringField('Название статуса', validators=[DataRequired()])

class DeliveryStatusForm(FlaskForm):
    name = StringField('Название статуса', validators=[DataRequired()])