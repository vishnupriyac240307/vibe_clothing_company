from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from db import db
from models.user import User
from utils.decorators import login_required, role_required
from utils.id_generator import generate_next_id
from utils.helpers import log_activity

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
@login_required
@role_required(['admin'])
def index():
    tab = request.args.get('tab', 'active').lower()
    search = request.args.get('search', '').strip()

    query = User.query

    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.user_id.ilike(f"%{search}%"))
        )

    if tab == 'archived':
        users = query.filter_by(is_active=False).order_by(User.created_at.desc()).all()
    else:
        users = query.filter_by(is_active=True).order_by(User.created_at.desc()).all()

    active_count = User.query.filter_by(is_active=True).count()
    archived_count = User.query.filter_by(is_active=False).count()

    return render_template(
        'users/index.html',
        users=[u.to_dict() for u in users],
        active_tab=tab,
        active_count=active_count,
        archived_count=archived_count,
        search=search
    )

@users_bp.route('/users/add', methods=['POST'])
@login_required
@role_required(['admin'])
def add_user():
    try:
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'staff').lower()

        if not username or not email or not password:
            flash('Username, Email and Password are required.', 'danger')
            return redirect(url_for('users.index'))

        if role not in ['admin', 'manager', 'staff']:
            role = 'staff'

        existing = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing:
            flash('Username or Email already exists.', 'danger')
            return redirect(url_for('users.index'))

        user_id = generate_next_id('user')
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            phone=phone,
            role=role,
            is_active=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        log_activity('Admin Create User', 'Users', f"Admin created user {username} ({user_id}) with role '{role.upper()}'.", record_id=user_id)
        flash(f"User {username} ({user_id}) created successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating user: {str(e)}", 'danger')

    return redirect(url_for('users.index'))

@users_bp.route('/users/change-role/<user_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def change_role(user_id):
    user = User.query.filter_by(user_id=user_id).first_or_404()
    new_role = request.form.get('role', 'staff').lower()

    if new_role not in ['admin', 'manager', 'staff']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('users.index'))

    # Prevent admin from demoting themselves
    if user.user_id == session.get('user_id') and new_role != 'admin':
        flash('You cannot change your own admin role.', 'danger')
        return redirect(url_for('users.index'))

    user.role = new_role
    db.session.commit()

    log_activity('Change User Role', 'Users', f"Changed role of user {user.username} ({user_id}) to '{new_role.upper()}'.", record_id=user_id)
    flash(f"Role for {user.username} updated to {new_role.upper()}.", 'success')

    return redirect(url_for('users.index'))

@users_bp.route('/users/toggle-status/<user_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def toggle_status(user_id):
    user = User.query.filter_by(user_id=user_id).first_or_404()

    if user.user_id == session.get('user_id'):
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('users.index'))

    user.is_active = not user.is_active
    status_str = 'Activated' if user.is_active else 'Deactivated'
    db.session.commit()

    log_activity('Toggle User Status', 'Users', f"User {user.username} ({user_id}) was {status_str}.", record_id=user_id)
    flash(f"User {user.username} has been {status_str}.", 'success')

    return redirect(url_for('users.index'))
