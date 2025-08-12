from models.order import Order
from extensions.db import db

class OrderRepository:
    @staticmethod
    def get_all():
        return Order.query.all()

    @staticmethod
    def get_by_id(order_id):
        return Order.query.get_or_404(order_id)

    @staticmethod
    def add(order, flush=False):
        db.session.add(order)
        if flush:
            db.session.flush()

    @staticmethod
    def delete(order):
        db.session.delete(order)
        db.session.commit()

    @staticmethod
    def commit():
        db.session.commit()
