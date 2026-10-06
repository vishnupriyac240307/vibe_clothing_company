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

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'inventory_bp',
    'products_bp',
    'production_bp',
    'batches_bp',
    'customers_bp',
    'suppliers_bp',
    'quality_bp',
    'shipments_bp',
    'analytics_bp',
    'users_bp',
    'activity_bp',
    'profile_bp',
    'reports_bp',
    'traceability_bp',
    'notifications_bp'
]
