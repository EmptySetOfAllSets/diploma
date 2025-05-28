# routes.py
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import Admin, Dish, Groc, Ingredient, Groc_type, Groc_unit, Dish_type, Client, Order_status, Order, Delivery, Delivery_status, Position
from forms import (ProductForm, DishForm, ProductTypeForm, UnitForm, DishTypeForm, 
                   IngredientForm, IngredientFormForDish, ClientForm, PositionForm, OrderForm,
                   DeliveryForm, DeliveryStatusForm, OrderStatusForm,)
from datetime import datetime, timedelta



def init_routes(app):
    @app.context_processor
    def inject_active_tab():
        return {'active_tab': request.args.get('tab', 'dishes')}
    

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for('admin_panel'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            admin = Admin.query.filter_by(username=username).first()
            
            if admin and admin.verify_password(password):
                login_user(admin)
                return redirect(url_for('admin_panel'))
            else:
                flash('Неверные учетные данные', 'danger')
        
        return render_template('admin/login.html')

    @app.route('/admin/logout')
    @login_required
    def admin_logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/admin')
    @login_required
    def admin_panel():
        return render_template('admin/dashboard.html')
    @app.route('/admin/menu')
    @login_required
    def admin_menu():
        active_tab = request.args.get('tab', 'dishes')
        search_query = request.args.get('search', '')
        show_all = request.args.get('show_all', 'false').lower() == 'true'
        
        # Инициализация переменных для всех вкладок
        dishes = products = types = units = ingredients = None
        
        if active_tab == 'dishes':
            
            query = Dish.query
            if not show_all:
                query = query.filter_by(avaliable=True)
            dishes = query.all()
            print (f"!!{query}")
            query = Dish.query.join(Dish.dish_type)
            if search_query:
                query = query.filter(
                    db.or_(
                        Dish.name.ilike(f'%{search_query}%'),
                        Dish_type.type.ilike(f'%{search_query}%')
                    )
                )
            dishes = query.all()
        
        elif active_tab == 'products':
            query = Groc.query.join(Groc.groc_type).join(Groc.groc_unit)
            if search_query:
                query = query.filter(
                    db.or_(
                        Groc.name.ilike(f'%{search_query}%'),
                        Groc_type.type.ilike(f'%{search_query}%'),
                        Groc_unit.unit.ilike(f'%{search_query}%')
                    )
                )
            products = query.all()
        
        elif active_tab == 'types':
            query = Groc_type.query
            if search_query:
                query = query.filter(Groc_type.type.ilike(f'%{search_query}%'))
            types = query.all()
        
        elif active_tab == 'units':
            query = Groc_unit.query
            if search_query:
                query = query.filter(Groc_unit.unit.ilike(f'%{search_query}%'))
            units = query.all()
        
        elif active_tab == 'ingredients':
            query = Ingredient.query.join(Ingredient.dish).join(Ingredient.groc)
            if search_query:
                query = query.filter(
                    db.or_(
                        Ingredient.description.ilike(f'%{search_query}%'),
                        Dish.name.ilike(f'%{search_query}%'),
                        Groc.name.ilike(f'%{search_query}%')
                    )
                )
            ingredients = query.all()
        
        return render_template(
            'admin/menu.html',
            active_tab=active_tab,
            dishes=dishes,
            show_all=show_all,
            products=products,
            types=types,
            units=units,
            ingredients=ingredients,
            search_query=search_query
        )
    # Product Types
    @app.route('/admin/add/product_type', methods=['GET', 'POST'])
    @login_required
    def add_product_type():
        form = ProductTypeForm()
        if form.validate_on_submit():
            product_type = Groc_type(type=form.type.data)
            db.session.add(product_type)
            db.session.commit()
            flash('Тип продукта успешно добавлен', 'success')
            return redirect(url_for('admin_menu', tab='types'))
        return render_template('admin/edit_form.html', form=form, title='Добавить тип продукта')

    @app.route('/admin/edit/type/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_type(id):
        product_type = Groc_type.query.get_or_404(id)
        form = ProductTypeForm(obj=product_type)
        if form.validate_on_submit():
            form.populate_obj(product_type)
            db.session.commit()
            flash('Тип продукта успешно обновлен', 'success')
            return redirect(url_for('admin_menu', tab='types'))
        return render_template('admin/edit_form.html', form=form, title='Редактировать тип продукта')

    @app.route('/admin/delete/type/<int:id>')
    @login_required
    def delete_type(id):
        try:
            product_type = Groc_type.query.get_or_404(id)
            db.session.delete(product_type)
            db.session.commit()
            flash('Тип продукта успешно удален', 'success')
        except Exception as e:
            db.session.rollback()
            print("!!!")
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        return redirect(url_for('admin_menu', tab='types'))

    # Units
    @app.route('/admin/add/unit', methods=['GET', 'POST'])
    @login_required
    def add_unit():
        form = UnitForm()
        if form.validate_on_submit():
            unit = Groc_unit(unit=form.unit.data)
            db.session.add(unit)
            db.session.commit()
            flash('Единица измерения успешно добавлена', 'success')
            return redirect(url_for('admin_menu', tab='units'))
        return render_template('admin/edit_form.html', form=form, title='Добавить единицу измерения')

    @app.route('/admin/edit/unit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_unit(id):
        unit = Groc_unit.query.get_or_404(id)
        form = UnitForm(obj=unit)
        if form.validate_on_submit():
            form.populate_obj(unit)
            db.session.commit()
            flash('Единица измерения успешно обновлена', 'success')
            return redirect(url_for('admin_menu', tab='units'))
        return render_template('admin/edit_form.html', form=form, title='Редактировать единицу измерения')

    @app.route('/admin/delete/unit/<int:id>')
    @login_required
    def delete_unit(id):
        try:
            unit = Groc_unit.query.get_or_404(id)
            db.session.delete(unit)
            db.session.commit()
            flash('Единица измерения успешно удалена', 'success')
        except Exception as e:
            db.session.rollback()
            print("!!!")
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        return redirect(url_for('admin_menu', tab='units'))

    # Products (Groc)
    @app.route('/admin/add/product', methods=['GET', 'POST'])
    @login_required
    def add_product():
        form = ProductForm()
        if form.validate_on_submit():
            product = Groc(
                name=form.name.data,
                groc_type_id=form.type_id.data,
                groc_unit_id=form.unit_id.data
            )
            db.session.add(product)
            db.session.commit()
            flash('Продукт успешно добавлен', 'success')
            return redirect(url_for('admin_menu', tab='products'))
        return render_template('admin/edit_form.html', form=form, title='Добавить продукт')

    @app.route('/admin/edit/product/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_product(id):
        product = Groc.query.get_or_404(id)
        form = ProductForm(obj=product)
        
        if form.validate_on_submit():
            new_type_id = int(form.type_id.data)
            new_unit_id = int(form.unit_id.data)
            
            print(f"Старые значения: type={product.groc_type_id}, unit={product.groc_unit_id}")
            print(f"Новые значения: type={new_type_id}, unit={new_unit_id}")
            
            if new_type_id != product.groc_type_id:
                product.groc_type_id = new_type_id
                print(f"Значение type_id после присвоения: {product.groc_type_id}")
                
            if new_unit_id != product.groc_unit_id:
                product.groc_unit_id = new_unit_id
                
            print(f"Состояние перед коммитом: {db.session.is_modified(product)}")
            db.session.commit()
            
            # Проверка после коммита
            updated = Groc.query.get(id)
            print(f"Фактическое значение в БД: type={updated.groc_type_id}, unit={updated.groc_unit_id}")
            
            flash('Продукт обновлен!', 'success')
            return redirect(url_for('admin_menu', tab='products'))
        
        return render_template('admin/edit_form.html', form=form, title='Редактировать продукт')    
        
        return render_template('admin/edit_form.html', form=form, title='Редактировать продукт')
        dish = Dish.query.get_or_404(id)
        form = DishForm(obj=dish)
        if form.validate_on_submit():
            form.populate_obj(dish)
            db.session.commit()
            flash('Блюдо успешно обновлено', 'success')
            return redirect(url_for('admin_menu', tab='dishes'))
        return render_template('admin/edit_form.html', form=form, title='Редактировать блюдо')

    @app.route('/admin/delete/product/<int:id>')
    @login_required
    def delete_product(id):
        try:
            product = Groc.query.get_or_404(id)
            db.session.delete(product)
            db.session.commit()
            flash('Продукт успешно удален', 'success')
        except Exception as e:
            db.session.rollback()
            print("!!!")
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        return redirect(url_for('admin_menu', tab='products'))

    # Dish Types
    @app.route('/admin/add/dishtype', methods=['GET', 'POST'])
    @login_required
    def add_dishtype():
        form = DishTypeForm()
        if form.validate_on_submit():
            dish_type = Dish_type(type=form.type.data)
            db.session.add(dish_type)
            db.session.commit()
            flash('Тип блюда успешно добавлен', 'success')
            return redirect(url_for('admin_menu', tab='dishes'))
        return render_template('admin/edit_form.html', form=form, title='Добавить тип блюда')

    @app.route('/admin/edit/dishtype/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_dishtype(id):
        dish_type = Dish_type.query.get_or_404(id)
        form = DishTypeForm(obj=dish_type)
        if form.validate_on_submit():
            form.populate_obj(dish_type)
            db.session.commit()
            flash('Тип блюда успешно обновлен', 'success')
            return redirect(url_for('admin_menu', tab='dishes'))
        return render_template('admin/edit_form.html', form=form, title='Редактировать тип блюда')

    @app.route('/admin/delete/dishtype/<int:id>')
    @login_required
    def delete_dishtype(id):
        try:
            dish_type = Dish_type.query.get_or_404(id)
            db.session.delete(dish_type)
            db.session.commit()
            flash('Тип блюда успешно удален', 'success')
        except Exception as e:
            db.session.rollback()
            print("!!!")
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        return redirect(url_for('admin_menu', tab='dishes'))

    # Dishes
    # @app.route('/admin/add/dish', methods=['GET', 'POST'])
    # @login_required
    # def add_dish():
    #     form = DishForm()
    #     if form.validate_on_submit():
    #         dish = Dish(
    #             name=form.name.data,
    #             price=form.price.data,
    #             dish_type_id=form.dish_type_id.data
    #         )
    #         db.session.add(dish)
    #         db.session.commit()
    #         flash('Блюдо успешно добавлено', 'success')
    #         return redirect(url_for('admin_menu', tab='dishes'))
    #     return render_template('admin/edit_form.html', form=form, title='Добавить блюдо')

    @app.route('/admin/edit/dish/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_dish(id):
        dish = Dish.query.get_or_404(id)
        form = DishForm(obj=dish)
        if form.validate_on_submit():
            form.populate_obj(dish)
            db.session.commit()
            flash('Блюдо успешно обновлено', 'success')
            return redirect(url_for('admin_menu', tab='dishes'))
        return render_template('admin/edit_form.html', form=form, title='Редактировать блюдо')

    @app.route('/admin/delete/dish/<int:id>')
    @login_required
    def delete_dish(id):
        try:
            dish = Dish.query.get_or_404(id)
            db.session.delete(dish)
            db.session.commit()
            flash('Блюдо успешно удалено', 'success')
        except Exception as e:
            db.session.rollback()
            print("!!!")
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        return redirect(url_for('admin_menu', tab='dishes'))

    # Ingredients
    @app.route('/admin/add/ingredient', methods=['GET', 'POST'])
    @login_required
    def add_ingredient():
        form = IngredientForm()
        if form.validate_on_submit():
            ingredient = Ingredient(
                dish_id=form.dish_id.data,
                groc_id=form.groc_id.data,
                amount=form.amount.data,
                description=form.description.data
            )
            db.session.add(ingredient)
            db.session.commit()
            flash('Ингредиент успешно добавлен', 'success')
            return redirect(url_for('admin_menu', tab='ingredients'))
        return render_template('admin/edit_form.html', form=form, title='Добавить ингредиент')

    @app.route('/admin/edit/ingredient/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_ingredient(id):
        ingredient = Ingredient.query.get_or_404(id)
        form = IngredientForm(obj=ingredient)
        if form.validate_on_submit():
            form.populate_obj(ingredient)
            db.session.commit()
            flash('Ингредиент успешно обновлен', 'success')
            return redirect(url_for('admin_menu', tab='ingredients'))
        return render_template('admin/edit_form.html', form=form, title='Редактировать ингредиент')

    @app.route('/admin/delete/ingredient/<int:id>')
    @login_required
    def delete_ingredient(id):
        try:
            ingredient = Ingredient.query.get_or_404(id)
            db.session.delete(ingredient)
            db.session.commit()
            flash('Ингредиент успешно удален', 'success')
        except Exception as e:
            db.session.rollback()
            print("!!!")
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        return redirect(url_for('admin_menu', tab='ingredients'))
    

    # Шаг 1: Создание блюда
    @app.route('/admin/add/dish', methods=['GET', 'POST'])
    @login_required
    def add_dish():
        form = DishForm()
        if form.validate_on_submit():
            dish = Dish(
                name=form.name.data,
                price=form.price.data,
                dish_type_id=form.dish_type_id.data,
                avaliable = True
            )
            db.session.add(dish)
            db.session.commit()
            return redirect(url_for('add_dish_ingredients', dish_id=dish.id))
        return render_template('admin/add_dish.html', form=form)

    # Шаг 2: Добавление ингредиентов
    @app.route('/admin/dish/<int:dish_id>/ingredients', methods=['GET', 'POST'])
    @login_required
    def add_dish_ingredients(dish_id):
        dish = Dish.query.get_or_404(dish_id)
        form = IngredientFormForDish()
        if request.method == 'GET' and 'search' in request.args:
            form.search.data = request.args.get('search')
            form._update_product_choices(form.search.data)

        if form.validate_on_submit():
            product = Groc.query.get(form.product.data)
            
            ingredient = Ingredient(
                dish_id=dish.id,
                groc_id=product.id,
                amount=form.amount.data,
                kkal=form.kkal.data,
                description=f"{product.name} для {dish.name}"
            )
            
            db.session.add(ingredient)
            db.session.commit()
            flash('Ингредиент добавлен!', 'success')
            return redirect(url_for('add_dish_ingredients', dish_id=dish.id))
        
        return render_template('admin/add_ingredients.html', 
                            dish=dish, 
                            form=form,
                            ingredients=dish.ingredients)
    
    @app.route('/admin/dish/toggle/<int:id>')
    @login_required
    def toggle_dish_status(id):
        dish = Dish.query.get_or_404(id)
        dish.avaliable = not dish.avaliable
        db.session.commit()
        flash(f'Блюдо "{dish.name}" теперь {"актуально" if dish.avaliable else "неактуально"}', 'success')
        return redirect(url_for('admin_menu', tab='dishes'))

    @app.route('/admin/clients-orders')
    @login_required
    def admin_clients_orders():
        active_tab = request.args.get('tab', 'clients')
        search_query = request.args.get('search', '').strip()
        
        today = datetime.utcnow().date()
        
        # Базовые запросы
        clients_query = Client.query
        orders_query = Order.query.filter(
            db.func.date(Order.created_at) == today
        )
        deliveries_query = Delivery.query
        order_statuses_query = Order_status.query
        delivery_statuses_query = Delivery_status.query
        
        # Применяем поиск если есть запрос
        if search_query:
            if active_tab == 'clients':
                clients_query = clients_query.filter(
                    db.or_(
                        Client.name.ilike(f'%{search_query}%'),
                        Client.phone.ilike(f'%{search_query}%')
                    )
                )
            elif active_tab == 'orders':
                orders_query = orders_query.join(Order.client).filter(
                    db.or_(
                        Order.name.ilike(f'%{search_query}%'),
                        Client.name.ilike(f'%{search_query}%'),
                        Client.phone.ilike(f'%{search_query}%')
                    )
                )
            elif active_tab == 'deliveries':
                deliveries_query = deliveries_query.filter(
                    db.or_(
                        Delivery.description.ilike(f'%{search_query}%'),
                        Delivery.adress.ilike(f'%{search_query}%')
                    )
                )
            elif active_tab == 'statuses':
                order_statuses_query = order_statuses_query.filter(
                    Order_status.name.ilike(f'%{search_query}%')
                )
                delivery_statuses_query = delivery_statuses_query.filter(
                    Delivery_status.name.ilike(f'%{search_query}%')
                )
        
        return render_template('admin/clients_orders.html',
                            active_tab=active_tab,
                            clients=clients_query.all(),
                            orders=orders_query.all(),
                            deliveries=deliveries_query.all(),
                            order_statuses=order_statuses_query.all(),
                            delivery_statuses=delivery_statuses_query.all())

    @app.route('/admin/archive/orders')
    @login_required
    def archive_orders():
        search_query = request.args.get('search', '').strip()
        today = datetime.utcnow().date()
        
        orders_query = Order.query.filter(
            db.func.date(Order.created_at) != today
        ).order_by(Order.created_at.desc())
        
        if search_query:
            orders_query = orders_query.join(Order.client).filter(
                db.or_(
                    Order.name.ilike(f'%{search_query}%'),
                    Client.name.ilike(f'%{search_query}%'),
                    Client.phone.ilike(f'%{search_query}%')
                )
            )
        
        return render_template('admin/archive_orders.html',
                            orders=orders_query.all(),
                            search_query=search_query)
    
    @app.route('/admin/clients/add', methods=['GET', 'POST'])
    @login_required
    def add_client():
        form = ClientForm()
        
        if form.validate_on_submit():
            client = Client(
                name=form.name.data,
                phone=form.phone.data
            )
            db.session.add(client)
            db.session.commit()
            flash('Клиент успешно добавлен', 'success')
            return redirect(url_for('admin_clients_orders', tab='clients'))
        
        return render_template('admin/edit_client.html', 
                            form=form,
                            title='Добавить клиента')

    @app.route('/admin/clients/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_client(id):
        client = Client.query.get_or_404(id)
        form = ClientForm(obj=client)
        
        if form.validate_on_submit():
            form.populate_obj(client)
            db.session.commit()
            flash('Данные клиента обновлены', 'success')
            return redirect(url_for('admin_clients_orders', tab='clients'))
        
        return render_template('admin/edit_client.html',
                            form=form,
                            title='Редактировать клиента',
                            client=client)

    @app.route('/admin/clients/delete/<int:id>', methods=['POST'])
    @login_required
    def delete_client(id):
        client = Client.query.get_or_404(id)
        print("@")
        if not client.can_be_deleted():
            flash('Нельзя удалить клиента с существующими заказами', 'danger')
            print("@@")
        else:
            try:
                db.session.delete(client)
                db.session.commit()
                print("@@@")
                flash('Клиент успешно удален', 'success')
            except Exception as e:
                db.session.rollback()
                print(f"!!!{str(e)}")
                flash(f'Ошибка при удалении: {str(e)}', 'danger')
        
        return redirect(url_for('admin_clients_orders', tab='clients'))
    @app.route('/admin/orders/add', methods=['GET', 'POST'])
    @login_required
    def add_order():
        form = OrderForm()
        
        if form.validate_on_submit():
            order = Order(
                name=form.name.data,
                price=form.price.data,
                created_at=form.created_at.data,
                delivery_time=form.delivery_time.data,
                client_id=form.client_id.data,
                delivery_id=form.delivery_id.data or None,
                order_status_id=form.order_status_id.data
            )
            db.session.add(order)
            db.session.commit()
            flash('Заказ успешно создан', 'success')
            return redirect(url_for('admin_clients_orders', tab='orders'))
        
        return render_template('admin/edit_order.html', 
                            form=form,
                            title='Создать заказ')

    @app.route('/admin/orders/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_order(id):
        order = Order.query.get_or_404(id)
        form = OrderForm(obj=order)
        
        if form.validate_on_submit():
            form.populate_obj(order)
            db.session.commit()
            flash('Заказ обновлен', 'success')
            return redirect(url_for('admin_clients_orders', tab='orders'))
        
        return render_template('admin/edit_order.html',
                            form=form,
                            title='Редактировать заказ',
                            order=order)
    
    @app.route('/admin/orders/delete/<int:id>', methods=['POST'])
    @login_required
    def delete_order(id):
        order = Order.query.get_or_404(id)
        
        try:
            # Удаляем связанные позиции
            Position.query.filter_by(order_id=id).delete()
            db.session.delete(order)
            db.session.commit()
            print(order)
            flash('Заказ удален', 'success')
        except Exception as e:
            db.session.rollback()
            print("!!!")
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        
        return redirect(url_for('admin_clients_orders', tab='orders'))    

    @app.route('/admin/positions/add/<int:order_id>', methods=['GET', 'POST'])
    @login_required
    def add_position(order_id):
        order = Order.query.get_or_404(order_id)
        form = PositionForm()
        form.dish_id.choices = [(d.id, f"{d.name} ({d.price} руб.)") for d in Dish.query.filter_by(avaliable=True)]
        
        if form.validate_on_submit():
            position = Position(
                order_id=order_id,
                dish_id=form.dish_id.data,
                price=form.price.data
            )
            db.session.add(position)
            
            # Обновляем общую сумму заказа
            order.price = sum(p.price for p in order.positions) 
            db.session.commit()
            
            flash('Позиция добавлена', 'success')
            return redirect(url_for('edit_order', id=order_id))
        
        return render_template('admin/edit_position.html',
                            form=form,
                            title='Добавить позицию',
                            order=order)

    @app.route('/admin/positions/delete/<int:id>', methods=['POST'])
    @login_required
    def delete_position(id):
        print ("test")
        try:
            print("init")
            position = Position.query.get_or_404(id)
            
            order_id = position.order_id
            order = Order.query.get(order_id)
            print (position,order)
            # Удаляем конкретную позицию
            db.session.delete(position)
            db.session.commit()  # Фиксируем удаление сразу

            # Перезагружаем заказ из БД для актуальных данных
            order = Order.query.get(order_id)
            
            if not order:  # Если заказ автоматически удалился
                flash('Заказ удалён', 'info')
                return redirect(url_for('admin_clients_orders', tab='orders'))
                
            # Обновляем сумму заказа
            order.price = sum(p.price for p in order.positions)
            db.session.commit()

            flash('Позиция удалена', 'success')
            return redirect(url_for('edit_order', id=order_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
            return redirect(url_for('edit_order', id=order_id))
    # Доставки
    @app.route('/admin/deliveries/add', methods=['GET', 'POST'])
    @login_required
    def add_delivery():
        form = DeliveryForm()
        form.delivery_status_id.choices = [(s.id, s.name) for s in Delivery_status.query.all()]
        
        if form.validate_on_submit():
            delivery = Delivery(
                description=form.description.data,
                adress=form.adress.data,
                delivery_status_id=form.delivery_status_id.data
            )
            db.session.add(delivery)
            db.session.commit()
            flash('Доставка успешно добавлена', 'success')
            return redirect(url_for('admin_clients_orders', tab='deliveries'))
        
        return render_template('admin/edit_delivery.html', 
                            form=form,
                            title='Добавить доставку')

    @app.route('/admin/deliveries/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_delivery(id):
        delivery = Delivery.query.get_or_404(id)
        form = DeliveryForm(obj=delivery)
        form.delivery_status_id.choices = [(s.id, s.name) for s in Delivery_status.query.all()]
        
        if form.validate_on_submit():
            form.populate_obj(delivery)
            db.session.commit()
            flash('Доставка обновлена', 'success')
            return redirect(url_for('admin_clients_orders', tab='deliveries'))
        
        return render_template('admin/edit_delivery.html',
                            form=form,
                            title='Редактировать доставку',
                            delivery=delivery)

    @app.route('/admin/deliveries/delete/<int:id>', methods=['POST'])
    @login_required
    def delete_delivery(id):
        delivery = Delivery.query.get_or_404(id)
        
        try:
            db.session.delete(delivery)
            db.session.commit()
            flash('Доставка удалена', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        
        return redirect(url_for('admin_clients_orders', tab='deliveries'))

    # Статусы заказов
    @app.route('/admin/order_statuses/add', methods=['GET', 'POST'])
    @login_required
    def add_order_status():
        form = OrderStatusForm()
        
        if form.validate_on_submit():
            status = Order_status(name=form.name.data)
            db.session.add(status)
            db.session.commit()
            flash('Статус заказа добавлен', 'success')
            return redirect(url_for('admin_clients_orders', tab='statuses'))
        
        return render_template('admin/edit_status.html', 
                            form=form,
                            title='Добавить статус заказа')

    @app.route('/admin/order_statuses/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_order_status(id):
        status = Order_status.query.get_or_404(id)
        form = OrderStatusForm(obj=status)
        
        if form.validate_on_submit():
            form.populate_obj(status)
            db.session.commit()
            flash('Статус заказа обновлен', 'success')
            return redirect(url_for('admin_clients_orders', tab='statuses'))
        
        return render_template('admin/edit_status.html',
                            form=form,
                            title='Редактировать статус заказа',
                            status=status)

    @app.route('/admin/order_statuses/delete/<int:id>', methods=['POST'])
    @login_required
    def delete_order_status(id):
        status = Order_status.query.get_or_404(id)
        
        try:
            db.session.delete(status)
            db.session.commit()
            flash('Статус заказа удален', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        
        return redirect(url_for('admin_clients_orders', tab='statuses'))

    # Статусы доставок
    @app.route('/admin/delivery_statuses/add', methods=['GET', 'POST'])
    @login_required
    def add_delivery_status():
        form = DeliveryStatusForm()
        
        if form.validate_on_submit():
            status = Delivery_status(name=form.name.data)
            db.session.add(status)
            db.session.commit()
            flash('Статус доставки добавлен', 'success')
            return redirect(url_for('admin_clients_orders', tab='statuses'))
        
        return render_template('admin/edit_status.html', 
                            form=form,
                            title='Добавить статус доставки')

    @app.route('/admin/delivery_statuses/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_delivery_status(id):
        status = Delivery_status.query.get_or_404(id)
        form = DeliveryStatusForm(obj=status)
        
        if form.validate_on_submit():
            form.populate_obj(status)
            db.session.commit()
            flash('Статус доставки обновлен', 'success')
            return redirect(url_for('admin_clients_orders', tab='statuses'))
        
        return render_template('admin/edit_status.html',
                            form=form,
                            title='Редактировать статус доставки',
                            status=status)

    @app.route('/admin/delivery_statuses/delete/<int:id>', methods=['POST'])
    @login_required
    def delete_delivery_status(id):
        status = Delivery_status.query.get_or_404(id)
        
        try:
            db.session.delete(status)
            db.session.commit()
            flash('Статус доставки удален', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        
        return redirect(url_for('admin_clients_orders', tab='statuses'))
    
# Основные маршруты сайта
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/for-you')
    def for_you():
        return render_template('for_you.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/order')
    def create_order():
        return render_template('create_order.html')