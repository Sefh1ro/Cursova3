from flask import Blueprint, request, jsonify
from flask_login import login_required
from services.finance_service import FinanceService

financial_bp = Blueprint('financial_bp', __name__, url_prefix='/api/financial')

@financial_bp.route('/', methods=['GET'])
@login_required
def get_financial_data():
    period = request.args.get('period', 'month')
    data = FinanceService.get_financial_data(period)
    return jsonify(data)
