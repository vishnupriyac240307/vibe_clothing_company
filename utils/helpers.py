from flask import session, request
from db import db
from models.activity import ActivityLog
from models.notification import Notification

def format_inr(amount):
    """
    Formats monetary numbers into Indian Rupee standard format:
    e.g. 799 -> ₹799.00
    1250000 -> ₹12,50,000.00
    NEVER uses USD ($) or EUR.
    """
    try:
        val = float(amount or 0.0)
    except (ValueError, TypeError):
        val = 0.0

    is_negative = val < 0
    val = abs(val)

    s, decimal_part = f"{val:.2f}".split('.')
    
    if len(s) <= 3:
        formatted_integer = s
    else:
        last3 = s[-3:]
        other = s[:-3]
        groups = []
        while len(other) > 2:
            groups.insert(0, other[-2:])
            other = other[:-2]
        if other:
            groups.insert(0, other)
        groups.append(last3)
        formatted_integer = ','.join(groups)

    result = f"₹{formatted_integer}.{decimal_part}"
    return f"-{result}" if is_negative else result

def log_activity(action, module, description, record_id=None, user_id=None):
    """Logs an application event into the activity_logs table."""
    if not user_id:
        user_id = session.get('username', 'System')
    
    ip_addr = request.remote_addr if request else '127.0.0.1'
    
    try:
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            module=module,
            record_id=str(record_id) if record_id else None,
            description=description,
            ip_address=ip_addr
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {e}")

def create_notification(title, message, ntype='info', link='#'):
    """Creates a system notification alert."""
    try:
        notif = Notification(
            title=title,
            message=message,
            type=ntype,
            link=link
        )
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
