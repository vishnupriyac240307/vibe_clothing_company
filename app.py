import os
from datetime import datetime, timezone
from flask import Flask, render_template, session

from config import Config
from db import db
from utils.helpers import format_inr
from werkzeug.security import generate_password_hash

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register Jinja2 template filters & globals
    app.jinja_env.filters['format_inr'] = format_inr

    @app.context_processor
    def inject_global_context():
        from models.notification import Notification
        from models.material import Material
        
        unread_notifs_count = 0
        low_stock_count = 0
        
        if 'user_id' in session:
            try:
                unread_notifs_count = Notification.query.filter_by(is_read=False).count()
                low_stock_count = Material.query.filter(Material.quantity <= Material.minimum_level).count()
            except Exception:
                pass

        return {
            'current_user': {
                'id': session.get('user_id'),
                'username': session.get('username', 'Guest'),
                'email': session.get('email', ''),
                'role': session.get('role', 'staff')
            },
            'unread_notifications_count': unread_notifs_count,
            'low_stock_count': low_stock_count,
            'currency_symbol': '₹'
        }

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.inventory import inventory_bp
    from routes.products import products_bp
    from routes.production import production_bp
    from routes.batches import batches_bp
    from routes.customers import customers_bp
    from routes.suppliers import suppliers_bp
    from routes.quality import quality_bp
    from routes.shipments import shipments_bp
    from routes.analytics import analytics_bp
    from routes.users import users_bp
    from routes.activity import activity_bp
    from routes.profile import profile_bp
    from routes.reports import reports_bp
    from routes.traceability import traceability_bp
    from routes.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(batches_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(quality_bp)
    app.register_blueprint(shipments_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(traceability_bp)
    app.register_blueprint(notifications_bp)

    # Register Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Auto-initialize database & seed data if empty
    with app.app_context():
        db.create_all()
        seed_db_if_empty()

    return app

def seed_db_if_empty():
    """Auto-seeds database with realistic manufacturing data on first launch."""
    from models.user import User
    from seed_data import populate_database

    if User.query.count() > 0:
        return # DB already expanded and seeded

    print("Initializing & seeding expanded Vibe Clothing ERP database...")
    populate_database()


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5001))
    if port == 5000:
        port = 5001
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError:
        alt_port = port + 1
        print(f"Port {port} is in use. Starting Vibe Clothing ERP on http://localhost:{alt_port}")
        app.run(host='0.0.0.0', port=alt_port, debug=False)



