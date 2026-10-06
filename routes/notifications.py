from flask import Blueprint, jsonify, request, render_template
from db import db
from models.notification import Notification
from utils.decorators import login_required

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
@login_required
def list_notifications():
    category = request.args.get('category')
    query = Notification.query.order_by(Notification.created_at.desc())
    if category == 'low_stock':
        query = query.filter(Notification.title.ilike('%stock%') | Notification.message.ilike('%stock%'))
    elif category == 'new_order':
        query = query.filter(Notification.title.ilike('%production%') | Notification.title.ilike('%order%'))
    elif category == 'shipment_pending':
        query = query.filter(Notification.title.ilike('%shipment%') | Notification.message.ilike('%shipment%'))
    
    notifications = query.all()
    return render_template('notifications/index.html', notifications=notifications, selected_category=category)

@notifications_bp.route('/api/notifications')
@login_required
def get_notifications():
    notifs = Notification.query.order_by(Notification.created_at.desc()).limit(20).all()
    unread_count = Notification.query.filter_by(is_read=False).count()
    return jsonify({
        'success': True,
        'unread_count': unread_count,
        'notifications': [n.to_dict() for n in notifs]
    })

@notifications_bp.route('/api/notifications/mark-read', methods=['POST'])
@notifications_bp.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_read():
    data = request.get_json(silent=True) or {}
    notif_id = data.get('id')

    if notif_id:
        notif = Notification.query.get(notif_id)
        if notif:
            notif.is_read = True
    else:
        Notification.query.filter_by(is_read=False).update({'is_read': True})

    db.session.commit()
    return jsonify({'success': True, 'status': 'ok'})

@notifications_bp.route('/api/notifications/delete/<int:notif_id>', methods=['POST', 'DELETE'])
@notifications_bp.route('/api/notifications/delete', methods=['POST', 'DELETE'])
@login_required
def delete_notification(notif_id=None):
    if not notif_id:
        data = request.get_json(silent=True) or {}
        notif_id = data.get('id')
    
    if notif_id:
        notif = Notification.query.get(notif_id)
        if notif:
            db.session.delete(notif)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Notification deleted'})
        return jsonify({'success': False, 'message': 'Notification not found'}), 404
    else:
        # Clear all notifications
        Notification.query.delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'All notifications cleared'})

@notifications_bp.route('/api/notifications/delete-all', methods=['POST', 'DELETE'])
@notifications_bp.route('/api/notifications/clear', methods=['POST', 'DELETE'])
@login_required
def clear_all_notifications():
    Notification.query.delete()
    db.session.commit()
    return jsonify({'success': True, 'message': 'All notifications cleared'})
