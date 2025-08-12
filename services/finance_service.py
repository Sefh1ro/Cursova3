from datetime import datetime, timedelta
from models.order import Order

class FinanceService:

    @staticmethod
    def get_financial_data(period: str):
        now = datetime.now()

        if period == 'day':
            labels = [(now - timedelta(days=i)).strftime('%d.%m') for i in range(6, -1, -1)]
            date_ranges = [now - timedelta(days=i) for i in range(6, -1, -1)]
        elif period == 'week':
            labels = [f"Тиждень {(now - timedelta(weeks=i)).isocalendar()[1]}" for i in range(5, -1, -1)]
            date_ranges = [now - timedelta(weeks=i) for i in range(5, -1, -1)]
        elif period == 'year':
            months = [(now - timedelta(days=30 * i)).strftime('%Y-%m') for i in range(11, -1, -1)]
            labels = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in months]
            date_ranges = [datetime.strptime(m, '%Y-%m') for m in months]
        else:  # default = 'month'
            labels = [(now - timedelta(days=30 * i)).strftime('%b') for i in range(5, -1, -1)]
            date_ranges = [now - timedelta(days=30 * i) for i in range(5, -1, -1)]

        revenue_data = []

        for date in date_ranges:
            if period == 'day':
                start_date = datetime(date.year, date.month, date.day)
                end_date = start_date + timedelta(days=1)

            elif period == 'week':
                start_date = date - timedelta(days=date.weekday())
                end_date = start_date + timedelta(days=6)
            elif period == 'year':
                start_date = datetime(date.year, date.month, 1)
                end_date = datetime(date.year + 1, 1, 1) - timedelta(days=1) if date.month == 12 else datetime(date.year, date.month + 1, 1) - timedelta(days=1)
            else:  # month
                start_date = datetime(date.year, date.month, 1)
                end_date = datetime(date.year + 1, 1, 1) - timedelta(days=1) if date.month == 12 else datetime(date.year, date.month + 1, 1) - timedelta(days=1)

            completed_orders = Order.query.filter(
                
                Order.status == True,
                Order.completion_date >= start_date,
                Order.completion_date < end_date
            ).all()

            period_revenue = sum(order.final_price or order.repair_price for order in completed_orders)
            revenue_data.append(period_revenue)

        return {
            'labels': labels,
            'datasets': [{
                'label': 'Дохід, грн',
                'data': revenue_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }],
            'total_revenue': sum(revenue_data)
        }
