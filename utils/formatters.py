def format_currency(amount):
    if amount is None:
        return "₹0.00"
    return f"₹{amount:,.2f}"

def format_number(val):
    if val is None:
        return "0"
    return f"{val:,}"

def status_badge_class(status):
    status_upper = str(status).upper()
    mapping = {
        'OK': 'badge-success',
        'READY': 'badge-success',
        'COMPLETED': 'badge-success',
        'PASS': 'badge-success',
        'DELIVERED': 'badge-success',
        'ACTIVE': 'badge-success',
        
        'LOW': 'badge-warning',
        'IN PROGRESS': 'badge-info',
        'IN_PROGRESS': 'badge-info',
        'PARTIALLY READY': 'badge-warning',
        'SHIPPED': 'badge-info',
        'IN TRANSIT': 'badge-info',
        'PACKED': 'badge-primary',
        
        'CRITICAL': 'badge-danger',
        'FAIL': 'badge-danger',
        'BLOCKED': 'badge-danger',
        'CANCELLED': 'badge-secondary',
        'DELAYED': 'badge-danger',
        'DEACTIVATED': 'badge-secondary',
        'URGENT': 'badge-danger'
    }
    return mapping.get(status_upper, 'badge-secondary')
