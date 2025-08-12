from models.phone import Phone
from extensions.db import db

class PhoneRepository:

    @staticmethod
    def add(phone):
        db.session.add(phone)

    @staticmethod
    def delete_by_order(order_id):
        Phone.query.filter_by(order_id=order_id).delete()
