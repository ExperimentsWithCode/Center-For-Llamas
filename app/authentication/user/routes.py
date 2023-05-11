from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

from .models import db, User

# Blueprint Configuration
user_bp = Blueprint(
    'user_bp', __name__,
    url_prefix='/user',
    template_folder='templates',
    static_folder='static'
)


"""Logged-in page routes."""
@user_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    """Logged-in User Dashboard."""
    return render_template(
        'dashboard.jinja2',
        title='Flask-Login Tutorial.',
        template='dashboard-template',
        current_user=current_user,
        body="You are now logged in!"
    )
