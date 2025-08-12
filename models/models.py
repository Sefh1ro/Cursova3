from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        # Якщо логін admin, встановлюємо права адміністратора
        if self.name == 'admin':
            self.is_admin = True
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    device_model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    device_condition = db.Column(db.Text, nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    received_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    completion_date = db.Column(db.DateTime)
    repair_price = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float)
    status = db.Column(db.Boolean, nullable=False, default=False)
    
    phones = db.relationship('Phone', backref='order', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'client_name': self.client_name,
            'device_model': self.device_model,
            'serial_number': self.serial_number,
            'device_condition': self.device_condition,
            'issue_description': self.issue_description,
            'received_date': self.received_date.strftime('%Y-%m-%d %H:%M') if self.received_date else None,
            'completion_date': self.completion_date.strftime('%Y-%m-%d %H:%M') if self.completion_date else None,
            'repair_price': self.repair_price,
            'final_price': self.final_price,
            'status': self.status,
            'phones': [phone.phone for phone in self.phones]
        }
    
class Phone(db.Model):
    __tablename__ = 'phones'
    
    phone = db.Column(db.String(20), primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
