from extensions.db import db
from datetime import datetime

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