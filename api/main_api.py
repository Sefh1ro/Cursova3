from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

main_bp = Blueprint('main_bp', __name__, url_prefix='/main')

@main_bp.route('/')
@login_required
def main():
    return render_template('main.html')
