from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import db
from models.user import User
from utils.id_generator import generate_next_id
from utils.helpers import log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter((User.username == username) | (User.email == username)).first()

        if not user or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            log_activity('Failed Login', 'Auth', f"Failed login attempt for username: {username}")
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            log_activity('Deactivated Login Attempt', 'Auth', f"Login attempt for deactivated user: {user.username}")
            return render_template('auth/login.html')

        # Set session details
        session.clear()
        session['user_id'] = user.user_id
        session['id'] = user.id
        session['username'] = user.username
        session['email'] = user.email
        session['role'] = user.role
        session.permanent = remember

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()


        log_activity('Login', 'Auth', f"User {user.username} ({user.role.upper()}) logged in successfully.", user_id=user.username)
        flash(f'Welcome back, {user.username}!', 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'staff').lower()

        # Enforce valid role registration (staff, manager, admin)
        if role not in ['staff', 'manager', 'admin']:
            role = 'staff'

        if not username or not email or not password:
            flash('All required fields must be filled out.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or Email is already registered.', 'danger')
            return render_template('auth/register.html')

        new_user = User(
            user_id=generate_next_id('user'),
            username=username,
            email=email,
            phone=phone,
            role=role,
            is_active=True
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        log_activity('User Self-Registration', 'Auth', f"New account created for {username} with role {role.upper()}.", user_id=username)
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'User')
    log_activity('Logout', 'Auth', f"User {username} logged out.", user_id=username)
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
