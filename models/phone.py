from extensions.db import db

class Phone(db.Model):
    __tablename__ = 'phones'
    
    phone = db.Column(db.String(20), primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)