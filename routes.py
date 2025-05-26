# routes.py
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import Admin, Dish, Groc, Ingredient, Groc_type, Groc_unit, Dish_type
from forms import ProductForm, DishForm, ProductTypeForm, UnitForm, DishTypeForm, IngredientForm



def init_routes(app):
    @app.context_processor
    def inject_active_tab():
        return {'active_tab': request.args.get('tab', 'dishes')}
    
    @app.route('/')
    def index():
        return render_template('index.html', title='Главная')

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
        
        # Инициализация переменных для всех вкладок
        dishes = products = types = units = ingredients = None
        
        if active_tab == 'dishes':
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
            products=products,
            types=types,
            units=units,
            ingredients=ingredients,
            search_query=search_query
        )
    # Product Types
    @app.route('/admin/add/type', methods=['GET', 'POST'])
    @login_required
    def add_type():
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
        product_type = Groc_type.query.get_or_404(id)
        db.session.delete(product_type)
        db.session.commit()
        flash('Тип продукта успешно удален', 'success')
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
        unit = Groc_unit.query.get_or_404(id)
        db.session.delete(unit)
        db.session.commit()
        flash('Единица измерения успешно удалена', 'success')
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
        product = Groc.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        flash('Продукт успешно удален', 'success')
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
        dish_type = Dish_type.query.get_or_404(id)
        db.session.delete(dish_type)
        db.session.commit()
        flash('Тип блюда успешно удален', 'success')
        return redirect(url_for('admin_menu', tab='dishes'))

    # Dishes
    @app.route('/admin/add/dish', methods=['GET', 'POST'])
    @login_required
    def add_dish():
        form = DishForm()
        if form.validate_on_submit():
            dish = Dish(
                name=form.name.data,
                price=form.price.data,
                dish_type_id=form.dish_type_id.data
            )
            db.session.add(dish)
            db.session.commit()
            flash('Блюдо успешно добавлено', 'success')
            return redirect(url_for('admin_menu', tab='dishes'))
        return render_template('admin/edit_form.html', form=form, title='Добавить блюдо')

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
        dish = Dish.query.get_or_404(id)
        db.session.delete(dish)
        db.session.commit()
        flash('Блюдо успешно удалено', 'success')
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
        ingredient = Ingredient.query.get_or_404(id)
        db.session.delete(ingredient)
        db.session.commit()
        flash('Ингредиент успешно удален', 'success')
        return redirect(url_for('admin_menu', tab='ingredients'))