from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

# Blueprint Configuration
home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

# Controller info
@home_bp.route('/', methods=['GET'])
def home():
    """Homepage."""
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.dashboard'))

    return render_template(
        'index.jinja2',
        title='Treasury Farming Manager',
        subtitle='Modeling effects of Treasury Farming.',
        template='home-template',
    )
