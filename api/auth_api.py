from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import AuthService

auth_bp = Blueprint('auth_bp', __name__, url_prefix='')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = AuthService.authenticate(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main_bp.index'))
        else:
            flash("Невірне імʼя користувача або пароль", 'error')

    return render_template('login.html')  # ← твой шаблон


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
