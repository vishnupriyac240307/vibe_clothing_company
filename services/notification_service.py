from db import db
from models.inventory import Material
from models.notification import Notification

def check_and_trigger_low_stock_notifications():
    """
    Scans all materials in inventory and generates Notifications for materials at LOW or CRITICAL status.
    Avoids duplicate notifications within short timeframes.
    """
    try:
        materials = Material.query.all()
        created_count = 0

        for mat in materials:
            status = mat.status
            if status in ['LOW', 'CRITICAL']:
                notif_type = 'critical_stock' if status == 'CRITICAL' else 'low_stock'
                title = f"{status} STOCK ALERT: {mat.name}"
                message = f"Material '{mat.name}' ({mat.material_code}) is at {mat.quantity} {mat.unit} (Min: {mat.min_level}, Critical: {mat.critical_level}). Reorder recommended."
                
                # Check if recent unread notification exists for this material code
                existing = Notification.query.filter(
                    Notification.message.like(f"%{mat.material_code}%"),
                    Notification.is_read == False
                ).first()

                if not existing:
                    notif = Notification(
                        title=title,
                        message=message,
                        notification_type=notif_type,
                        link='/inventory'
                    )
                    db.session.add(notif)
                    created_count += 1

        if created_count > 0:
            db.session.commit()

        return created_count
    except Exception as e:
        db.session.rollback()
        print(f"Error checking low stock notifications: {e}")
        return 0
