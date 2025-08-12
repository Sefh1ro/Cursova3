from flask import Blueprint, redirect, url_for
from flask_login import login_required

root_bp = Blueprint('root_bp', __name__)

@root_bp.route('/')
@login_required
def root():
    return redirect(url_for('main_bp.main'))
