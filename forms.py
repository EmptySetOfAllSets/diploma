from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from models import Groc_type, Groc_unit, Dish_type, Groc, Dish, Ingredient

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