# app.py
from flask import Flask
from dotenv import load_dotenv
import os
from extensions import db, login_manager

# Загрузка переменных окружения
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'

    # Импорт моделей и маршрутов
    with app.app_context():
        from models import Admin
        db.create_all()  # Создаст таблицы, если их нет

        @login_manager.user_loader
        def load_user(user_id):
            return Admin.query.get(int(user_id))

        from routes import init_routes
        init_routes(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG'), host='0.0.0.0')