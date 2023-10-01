from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from app.home.content.nerd_stuff import nerd_stuff
from app.home.content.to_do import to_do

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


    return render_template(
        'index.jinja2',
        title='The Center For Llamas who want to Curve good',
        subtitle='and learn to do governance stuff good too.',
        template='home-template',
        nerd_stuff = nerd_stuff,
        to_do = to_do

    )
