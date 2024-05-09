from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for

import random

from app.address_book.actors.models import df_roles
from app.address_book.gauges.models import df_gauge_book

from app.utilities.utility import get_address_profile

from app.home.forms import EntryForm

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
        df_roles = df_roles
    )

@address_book_bp.route('/show/<string:actor_addr>', methods=['GET'])
def show_roles(actor_addr):
    """Shows An Address's role's"""

    return render_template(
        'directory_show_roles.jinja2',
        title='Directory: Show Roles',
        template='directory',
        body="",
        actor_profile = get_address_profile(app.config['df_roles'], actor_addr)
    )

@address_book_bp.route('/gauges/', methods=['GET'])
def gauge_index():
    """Homepage."""

    return render_template(
        'directory_gauges.jinja2',
        title='Directory Gauges',
        template='directory',
        body="",
        df_gauge_book = df_gauge_book
    )

@address_book_bp.route('/random_roles/', methods=['GET'])
def random_roles():
    """Shows a random Address"""
    unique_addresses = df_roles.address.unique()
    random_index = random.randint(0,len(unique_addresses)-1)
    actor_addr = list(unique_addresses)[random_index]
    return redirect(url_for('address_book_bp.show_roles', actor_addr=actor_addr))


@address_book_bp.route('/search/<string:search_target>', methods=['GET'])
def search(search_target):
    form = EntryForm()
    """Shows a results of search"""
    df_roles = app.config['df_roles']
    df_gauge_registry = app.config['df_curve_gauge_registry']
    roles = df_roles[
        (df_roles['address'].str.contains(search_target, case=False)) |
        (df_roles['known_as'].str.contains(search_target, case=False))
        ]
    gauges = df_gauge_registry[
        (df_gauge_registry['gauge_addr'].str.contains(search_target)) |
        (df_gauge_registry['pool_addr'].str.contains(search_target)) |
        (df_gauge_registry['gauge_name'].str.contains(search_target, case=False)) |
        (df_gauge_registry['pool_name'].str.contains(search_target, case=False)) 
        ]
    return render_template(
        'search_results.jinja2',
        title='Search Results',
        template='search-results',
        body="search_target",
        roles = roles,
        gauges = gauges,
        form = form,
    )
    
    # return redirect(url_for('address_book_bp.show_roles', actor_addr=actor_addr))
