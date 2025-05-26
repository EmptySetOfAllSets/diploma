

from app import create_app
from datetime import datetime, timedelta
import random
from extensions import db
from models import (
    Admin, Groc_type, Groc_unit, Groc, Ingredient, 
    Dish, Dish_type, Position, Order, Client, Delivery,
    Order_status, Delivery_status
)

def create_test_data():
    app = create_app()
    with app.app_context():
        # Очистка всех данных
        db.drop_all()
        db.create_all()

        
        types = [
            Groc_type(type="Овощи"),
            Groc_type(type="Фрукты"),
            Groc_type(type="Мясо"),
            Groc_type(type="Молочные"),
            Groc_type(type="Бакалея")
        ]
        db.session.add_all(types)

        # 3. Создаем единицы измерения
        units = [
            Groc_unit(unit="г"),
            Groc_unit(unit="кг"),
            Groc_unit(unit="мл"),
            Groc_unit(unit="л"),
            Groc_unit(unit="шт")
        ]
        db.session.add_all(units)
        db.session.commit()

        # 4. Создаем продукты
        products = [
            Groc(name="Помидор", groc_type_id=1, groc_unit_id=5),
            Groc(name="Огурец", groc_type_id=1, groc_unit_id=5),
            Groc(name="Курица", groc_type_id=3, groc_unit_id=1),
            Groc(name="Говядина", groc_type_id=3, groc_unit_id=1),
            Groc(name="Молоко", groc_type_id=4, groc_unit_id=4),
            Groc(name="Рис", groc_type_id=5, groc_unit_id=2)
        ]
        db.session.add_all(products)

        # 5. Создаем типы блюд
        dish_types = [
            Dish_type(type="Супы"),
            Dish_type(type="Салаты"),
            Dish_type(type="Гарниры"),
            Dish_type(type="Основные блюда"),
            Dish_type(type="Десерты")
        ]
        db.session.add_all(dish_types)
        db.session.commit()

        # 6. Создаем блюда
        dishes = [
            Dish(name="Салат Цезарь", price=350, avaliable=True, dish_type_id=2),
            Dish(name="Куриный суп", price=250, avaliable=True, dish_type_id=1),
            Dish(name="Говяжий стейк", price=550, avaliable=True, dish_type_id=4),
            Dish(name="Рис отварной", price=150, avaliable=True, dish_type_id=3),
            Dish(name="Молочный коктейль", price=200, avaliable=False, dish_type_id=5)
        ]
        db.session.add_all(dishes)
        db.session.commit()

        # 7. Создаем ингредиенты
        ingredients = [
            Ingredient(amount=200, kkal=165.5, description="Курица для салата",
                      groc_id=3, dish_id=1),
            Ingredient(amount=2, kkal=30.0, description="Помидоры для салата",
                      groc_id=1, dish_id=1),
            Ingredient(amount=300, kkal=220.0, description="Курица для супа",
                      groc_id=3, dish_id=2),
            Ingredient(amount=150, kkal=180.0, description="Говядина для стейка",
                      groc_id=4, dish_id=3),
            Ingredient(amount=100, kkal=130.0, description="Рис для гарнира",
                      groc_id=6, dish_id=4),
            Ingredient(amount=200, kkal=250.0, description="Молоко для коктейля",
                      groc_id=5, dish_id=5)
        ]
        db.session.add_all(ingredients)

        # 8. Создаем статусы заказов
        order_statuses = [
            Order_status(name="Новый"),
            Order_status(name="В обработке"),
            Order_status(name="Готовится"),
            Order_status(name="Готов к выдаче"),
            Order_status(name="Выполнен"),
            Order_status(name="Отменен")
        ]
        db.session.add_all(order_statuses)

        # 9. Создаем статусы доставки
        delivery_statuses = [
            Delivery_status(name="Ожидает обработки"),
            Delivery_status(name="Передан курьеру"),
            Delivery_status(name="В пути"),
            Delivery_status(name="Доставлен"),
            Delivery_status(name="Отменен")
        ]
        db.session.add_all(delivery_statuses)
        db.session.commit()

        # 10. Создаем клиентов
        clients = [
            Client(name="Иван Иванов", phone="+79161234567"),
            Client(name="Петр Петров", phone="+79167654321"),
            Client(name="Ольга Сидорова", phone="+79169998877")
        ]
        db.session.add_all(clients)

        # 11. Создаем варианты доставки (сначала без статусов)
        deliveries = [
            Delivery(description="Самовывоз", adress="ул. Пушкина, 10"),
            Delivery(description="Курьером", adress="ул. Лермонтова, 15"),
            Delivery(description="Доставка в офис", adress="ул. Гоголя, 20")
        ]
        db.session.add_all(deliveries)
        db.session.commit()

        # 12. Назначаем статусы доставкам
        for i, delivery in enumerate(Delivery.query.all()):
            delivery.delivery_status_id = random.randint(1, len(delivery_statuses))
        db.session.commit()

        # 13. Создаем заказы
        orders = []
        for i in range(5):
            order = Order(
                name=f"Заказ #{i+1}",
                price=random.randint(500, 2000),
                client_id=random.randint(1, len(clients)),
                delivery_id=random.randint(1, len(deliveries)),
                order_status_id=random.randint(1, len(order_statuses))
            )
            orders.append(order)
        
        db.session.add_all(orders)
        db.session.commit()

        # 14. Создаем позиции в заказах
        positions = []
        for order in orders:
            for _ in range(random.randint(1, 3)):
                positions.append(
                    Position(
                        price=random.randint(150, 600),
                        order_id=order.id,
                        dish_id=random.randint(1, len(dishes))
                    )
                )
        db.session.add_all(positions)
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


