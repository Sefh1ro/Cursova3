from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.models import db, User, Order, Phone
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__, static_folder='styles')
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:kou784438@localhost:5432/service_crm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки'
login_manager.login_message_category = 'info'

# Декоратор для перевірки прав адміністратора
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('У вас немає прав для доступу до цієї сторінки', 'error')
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        print(f"Помилка при завантаженні користувача: {e}")
        return None

@app.route('/')
@login_required
def index():
    return redirect(url_for('main'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(name=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main')
            return redirect(next_page)
        else:
            flash('Невірне ім\'я користувача або пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/main')
@login_required
def main():
    return render_template('main.html')

@app.route('/admin')
@login_required
@admin_required
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)


# @app.route('/admin')
# @login_required
# def admin():
#     if not current_user.is_admin:
#         flash('У вас немає прав для доступу до цієї сторінки', 'error')
#         return redirect(url_for('main'))
    
#     users = User.query.all()
#     return render_template('admin.html', users=users)

# API для управління користувачами
@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name} for user in users])

@app.route('/api/users', methods=['POST'])
@login_required
def add_user():
    data = request.json
    if not data or 'name' not in data or 'password' not in data:
        return jsonify({'error': 'Недостатньо даних'}), 400
    
    if User.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Користувач вже існує'}), 400
    
    user = User(name=data['name'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'id': user.id, 'name': user.name}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    if 'name' in data:
        user.name = data['name']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({'id': user.id, 'name': user.name})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    return '', 204

# API для управління замовленнями
@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    orders = Order.query.all()
    result = [order.to_dict() for order in orders]
    return jsonify(result)

@app.route('/api/orders', methods=['POST'])
@login_required
def add_order():
    data = request.json
    
    order = Order(
        client_name=data['client_name'],
        device_model=data['device_model'],
        serial_number=data['serial_number'],
        device_condition=data['device_condition'],
        issue_description=data['issue_description'],
        repair_price=float(data['repair_price']),
        received_date=datetime.now()
    )
    
    db.session.add(order)
    db.session.flush()  # Щоб отримати ID замовлення
    
    # Додавання телефонів
    if 'phones' in data and data['phones']:
        for phone in data['phones']:
            phone_record = Phone(phone=phone, order_id=order.id)
            db.session.add(phone_record)
    
    db.session.commit()
    
    return jsonify({'id': order.id}), 201

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.json
    
    for key, value in data.items():
        if key == 'phones':
            # Видалення існуючих телефонів
            Phone.query.filter_by(order_id=order.id).delete()
            
            # Додавання нових телефонів
            for phone in value:
                phone_record = Phone(phone=phone, order_id=order.id)
                db.session.add(phone_record)
        elif key == 'completion_date' and value:
            setattr(order, key, datetime.strptime(value, '%Y-%m-%d %H:%M'))
        elif key != 'id':
            setattr(order, key, value)
    
    db.session.commit()
    
    return jsonify({'id': order.id})

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    db.session.delete(order)
    db.session.commit()
    
    return '', 204

@app.route('/init_db')
def init_db():
    db.create_all()
    
    # Створення першого адміністратора, якщо немає користувачів
    if not User.query.first():
        admin = User(name='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        return 'База даних ініціалізована, створено користувача admin з паролем admin'
    
    return 'База даних ініціалізована'

@app.route('/api/financial', methods=['GET'])
@login_required
def get_financial_data():
    # Отримання параметру періоду з запиту
    period = request.args.get('period', 'month')
    
    # Поточна дата
    now = datetime.now()
    
    # Визначення початкової дати залежно від періоду
    if period == 'day':
        # Отримати дані за останні 7 днів
        labels = [(now - timedelta(days=i)).strftime('%d.%m') for i in range(6, -1, -1)]
        date_ranges = [(now - timedelta(days=i)) for i in range(6, -1, -1)]
    elif period == 'week':
        # Отримати дані за останні 6 тижнів
        labels = [f"Тиждень {(now - timedelta(weeks=i)).isocalendar()[1]}" for i in range(5, -1, -1)]
        date_ranges = [(now - timedelta(weeks=i)) for i in range(5, -1, -1)]
    elif period == 'year':
        # Отримати дані за останні 12 місяців
        months = []
        for i in range(11, -1, -1):
            month_date = now - timedelta(days=30*i)
            months.append(month_date.strftime('%Y-%m'))
            
        labels = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in months]
        date_ranges = [datetime.strptime(m, '%Y-%m') for m in months]
    else:  # month - за замовчуванням
        # Отримати дані за останні 6 місяців
        labels = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30*i)
            labels.append(month_date.strftime('%b'))
        date_ranges = [(now - timedelta(days=30*i)) for i in range(5, -1, -1)]
    
    # Зібрання даних доходів
    revenue_data = []
    
    # Для кожного періоду
    for i, date in enumerate(date_ranges):
        # Визначення вікна запиту
        if period == 'day':
            # Для одного дня
            start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        elif period == 'week':
            # Для тижня
            start_date = date - timedelta(days=date.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'year':
            # Для місяця у році
            start_date = datetime(date.year, date.month, 1)
            if date.month == 12:
                end_date = datetime(date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(date.year, date.month + 1, 1) - timedelta(days=1)
        else:  # month
            # Для місяця
            start_date = datetime(date.year, date.month, 1)
            if date.month == 12:
                end_date = datetime(date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(date.year, date.month + 1, 1) - timedelta(days=1)
        
        # Отримання суми завершених замовлень за період
        completed_orders = Order.query.filter(
            Order.status == True,
            Order.completion_date.between(start_date, end_date)
        ).all()
        
        # Розрахунок доходу
        period_revenue = sum(order.final_price or order.repair_price for order in completed_orders)
        revenue_data.append(period_revenue)
    
    # Розрахунок загального доходу для вибраного періоду
    total_revenue = sum(revenue_data)
    
    return jsonify({
        'labels': labels,
        'datasets': [{
            'label': 'Дохід, грн',
            'data': revenue_data,
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        }],
        'total_revenue': total_revenue
    })

if __name__ == '__main__':
    app.run(debug=True)
