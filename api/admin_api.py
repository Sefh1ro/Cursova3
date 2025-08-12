from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from core.auth_utils import admin_required
from models.user import User

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/admin')
@login_required
@admin_required
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)