

from app import create_app
from extensions import db
from models import Admin, Groc_type, Groc_unit, Groc, Ingredient, Dish, Dish_type

def create_test_data():
    app = create_app()
    with app.app_context():
        # Очистка всех данных
        db.drop_all()
        db.create_all()

        # Добавляем типы продуктов
        veg_type = Groc_type(type="Овощи")
        fruit_type = Groc_type(type="Фрукты")
        meat_type = Groc_type(type="Мясо")
        
        # Добавляем единицы измерения
        gram_unit = Groc_unit(unit="г")
        ml_unit = Groc_unit(unit="мл")
        piece_unit = Groc_unit(unit="шт")
        
        db.session.add_all([veg_type, fruit_type, meat_type, gram_unit, ml_unit, piece_unit])
        db.session.commit()

        # Добавляем продукты
        tomato = Groc(name="Помидор", groc_type_id=veg_type.id, groc_unit_id=piece_unit.id)
        chicken = Groc(name="Курица", groc_type_id=meat_type.id, groc_unit_id=gram_unit.id)
        potato = Groc(name="Картофель", groc_type_id=veg_type.id, groc_unit_id=gram_unit.id)
        
        db.session.add_all([tomato, chicken, potato])
        db.session.commit()

        # Добавляем типы блюд
        main_dish = Dish_type(type="Основное")
        soup = Dish_type(type="Суп")
        
        db.session.add_all([main_dish, soup])
        db.session.commit()

        # Добавляем блюда
        salad = Dish(name="Салат Цезарь", price=350.0, dish_type_id=main_dish.id)
        soup_chicken = Dish(name="Куриный суп", price=250.0, dish_type_id=soup.id)
        
        db.session.add_all([salad, soup_chicken])
        db.session.commit()

        # Добавляем ингредиенты
        ing1 = Ingredient(
            amount=200, kkal=165.5, description="Курица для салата",
            groc_id=chicken.id, dish_id=salad.id
        )
        ing2 = Ingredient(
            amount=2, kkal=30.0, description="Помидоры для салата",
            groc_id=tomato.id, dish_id=salad.id
        )
        ing3 = Ingredient(
            amount=300, kkal=220.0, description="Курица для супа",
            groc_id=chicken.id, dish_id=soup_chicken.id
        )
        
        db.session.add_all([ing1, ing2, ing3])
        db.session.commit()

        # Добавляем админа
        admin = Admin(username="admin")
        admin.password = "admin123"  # Пароль хешируется автоматически
        db.session.add(admin)
        db.session.commit()
        name = input("Введите имя администратора: ")
        password = input("Задайте пароль: ")
        new_admin = Admin(username=name)
        new_admin.password = password  # Здесь происходит хеширование
        db.session.add(new_admin)
        db.session.commit()
        print("Администратор создан")
        print("Тестовые данные успешно добавлены!")

if __name__ == '__main__':
    create_test_data()


