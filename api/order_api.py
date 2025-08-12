from flask import Blueprint, request, jsonify
from flask_login import login_required
from services.order_service import OrderService

order_bp = Blueprint('order_bp', __name__, url_prefix='/api/orders')

@order_bp.route('/', methods=['GET'])
@login_required
def get_orders():
    return jsonify(OrderService.get_all_orders())

@order_bp.route('/', methods=['POST'])
@login_required
def add_order():
    data = request.get_json()
    new_order = OrderService.create_order(data)
    return jsonify({'id': new_order.id}), 201

@order_bp.route('/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    data = request.get_json()
    updated_order = OrderService.update_order(order_id, data)
    return jsonify({'id': updated_order.id})

@order_bp.route('/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    OrderService.delete_order(order_id)
    return '', 204
