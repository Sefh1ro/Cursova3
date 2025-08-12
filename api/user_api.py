from flask import Blueprint, request, jsonify
from flask_login import login_required
from services.user_service import UserService

user_bp = Blueprint('user_bp', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
@login_required
def get_users():
    users = UserService.get_all_users()
    return jsonify([{'id': u.id, 'name': u.name} for u in users])

@user_bp.route('/', methods=['POST'])
@login_required
def add_user():
    data = request.get_json()
    if not data or 'name' not in data or 'password' not in data:
        return jsonify({'error': 'Недостатньо даних'}), 400
    
    result = UserService.create_user(data['name'], data['password'])
    if result is None:
        return jsonify({'error': 'Користувач вже існує'}), 400
    
    return jsonify({'id': result.id, 'name': result.name}), 201

@user_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    updated = UserService.update_user(user_id, data)
    return jsonify({'id': updated.id, 'name': updated.name})

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    UserService.delete_user(user_id)
    return '', 204
