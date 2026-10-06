from functools import wraps
from flask import session, redirect, url_for, flash, request, render_template, jsonify
from models.user import User
from db import db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login'))
            
            user_role = session.get('user_role', 'Supervisor')
            # Manager role mapping for backward compatibility if present in session
            if user_role == 'Manager':
                user_role = 'Supervisor'
            if user_role not in roles:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Unauthorized action for role: ' + user_role}), 403
                return render_template('errors/403.html', user_role=user_role, required_roles=roles), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_activity(user_id, action, module, record_id=None, description=None):
    # Activity logging disabled per prompt requirement
    pass

