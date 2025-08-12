from datetime import datetime
from repositories.order_repository import OrderRepository
from repositories.phone_repository import PhoneRepository
from models.order import Order
from models.phone import Phone

class OrderService:

    @staticmethod
    def get_all_orders():
        orders = OrderRepository.get_all()
        return [order.to_dict() for order in orders]

    @staticmethod
    def create_order(data):
        order = Order(
            client_name=data['client_name'],
            device_model=data['device_model'],
            serial_number=data['serial_number'],
            device_condition=data['device_condition'],
            issue_description=data['issue_description'],
            repair_price=float(data['repair_price']),
            received_date=datetime.now()
        )

        OrderRepository.add(order, flush=True)

        phones = data.get('phones', [])
        for phone in phones:
            phone_record = Phone(phone=phone, order_id=order.id)
            PhoneRepository.add(phone_record)

        OrderRepository.commit()
        return order

    @staticmethod
    def update_order(order_id, data):
        order = OrderRepository.get_by_id(order_id)

        for key, value in data.items():
            if key == 'phones':
                PhoneRepository.delete_by_order(order.id)
                for phone in value:
                    phone_record = Phone(phone=phone, order_id=order.id)
                    PhoneRepository.add(phone_record)
            elif key == 'completion_date' and value:
                order.completion_date = datetime.strptime(value, '%Y-%m-%d %H:%M')
            elif key != 'id':
                setattr(order, key, value)

        OrderRepository.commit()
        return order

    @staticmethod
    def delete_order(order_id):
        order = OrderRepository.get_by_id(order_id)
        OrderRepository.delete(order)
