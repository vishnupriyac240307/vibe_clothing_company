from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import db
from models.user import User
from utils.decorators import login_required
from utils.helpers import log_activity

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def index():
    user = User.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if email and email != user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash('Email is already in use.', 'danger')
                return redirect(url_for('profile.index'))
            user.email = email
            session['email'] = email

        user.phone = phone

        if new_password:
            if not current_password or not user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('profile.index'))
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('profile.index'))
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return redirect(url_for('profile.index'))
            user.set_password(new_password)
            flash('Password updated successfully!', 'success')

        db.session.commit()
        log_activity('Update Profile', 'Profile', f"User {user.username} updated profile information.", user_id=user.username)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.index'))

    return render_template('profile/index.html', user=user.to_dict())
