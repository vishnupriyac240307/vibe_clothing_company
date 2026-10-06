from flask import Blueprint, render_template, request
from models.activity import ActivityLog
from utils.decorators import login_required, role_required

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/activity')
@login_required
@role_required(['admin', 'manager'])
def index():
    module_filter = request.args.get('module', '').strip()
    user_filter = request.args.get('user', '').strip()
    search = request.args.get('search', '').strip()

    query = ActivityLog.query

    if search:
        query = query.filter(
            (ActivityLog.description.ilike(f"%{search}%")) |
            (ActivityLog.action.ilike(f"%{search}%")) |
            (ActivityLog.user_id.ilike(f"%{search}%")) |
            (ActivityLog.record_id.ilike(f"%{search}%"))
        )

    if module_filter:
        query = query.filter(ActivityLog.module == module_filter)
    if user_filter:
        query = query.filter(ActivityLog.user_id == user_filter)

    logs = query.order_by(ActivityLog.timestamp.desc()).limit(200).all()

    modules = ['Inventory', 'Products', 'Production', 'Batches', 'Quality', 'Shipments', 'Auth', 'Users', 'Customers', 'Suppliers']

    return render_template(
        'activity/index.html',
        logs=[l.to_dict() for l in logs],
        modules=modules,
        search=search,
        selected_module=module_filter,
        selected_user=user_filter
    )
