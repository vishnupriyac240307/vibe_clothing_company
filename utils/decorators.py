from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized authentication required', 'success': False}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'Unauthorized authentication required', 'success': False}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user_role = session.get('role', 'staff').lower()
            allowed = [r.lower() for r in allowed_roles]
            
            if user_role not in allowed:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'Forbidden: You do not have permission to perform this action.',
                        'success': False
                    }), 403
                return render_template('errors/403.html'), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
