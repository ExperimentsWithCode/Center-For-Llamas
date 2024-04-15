from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for

import random

from app.address_book.actors.models import df_actors
from app.utilities.utility import get_address_profile

address_book_bp = Blueprint(
    'address_book_bp', __name__,
    url_prefix='/directory/',
    template_folder='templates',
    static_folder='static'
)

# @address_book_bp.route('/', methods=['GET'])
# def home():
#     """Homepage."""
    
#     return redirect(url_for('home_bp.home'))


@address_book_bp.route('/', methods=['GET'])
def index():
    """Homepage."""


    return render_template(
        'directory.jinja2',
        title='Directory',
        template='directory',
        body="",
        df_actors = df_actors
    )

@address_book_bp.route('/show/<string:actor_addr>', methods=['GET'])
def show_roles(actor_addr):
    """Shows An Address's role's"""

    return render_template(
        'directory_show_roles.jinja2',
        title='Directory: Show Roles',
        template='directory',
        body="",
        actor_profile = get_address_profile(app.config['df_actors'], actor_addr)
    )

@address_book_bp.route('/random_roles/', methods=['GET'])
def random_roles():
    """Shows a random Address"""
    unique_addresses = df_actors.address.unique()
    random_index = random.randint(0,len(unique_addresses)-1)
    actor_addr = list(unique_addresses)[random_index]
    return redirect(url_for('address_book_bp.show_roles', actor_addr=actor_addr))
