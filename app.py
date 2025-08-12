import os
from flask import Flask
from config import Config
from extensions import db, login_manager
from api.root_api import root_bp
from api.user_api import user_bp
from api.order_api import order_bp
from api.auth_api import auth_bp
from api.main_api import main_bp
from api.admin_api import admin_bp
from api.financial_api import financial_bp


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:kou784438@localhost:5432/service_crm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(root_bp)
app.register_blueprint(user_bp)
app.register_blueprint(order_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(financial_bp)


if __name__ == '__main__':
    app.run(debug=True)
