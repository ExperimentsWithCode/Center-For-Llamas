from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for

from app.address_book.actors.models import df_actors

address_book_bp = Blueprint(
    'address_book_bp', __name__,
    url_prefix='/address_book/',
    template_folder='templates',
    static_folder='static'
)

@address_book_bp.route('/', methods=['GET'])
def home():
    """Homepage."""
    # Bypass if user is logged in


    return redirect(url_for('home_bp.home'))
