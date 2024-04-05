import os
from datetime import datetime as dt

from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from app.home.content.nerd_stuff import nerd_stuff
from app.home.content.to_do import to_do

from app.data.data_manager import Manager
from .forms import DataManagerForm
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




@home_bp.route('/data/male_models', methods=['GET','POST'])
def male_models():
    """Data Management in site."""
    # Bypass if user is logged in
    form = DataManagerForm()
    manager_config = {
        # Curve
        'gauge_to_lp_map': False,
        'curve_locker': False,
        'curve_gauge_votes': False,
        'curve_gauge_rounds': False,
        
        'curve_liquidity': False, 
        
        # Convex
        'convex_locker': False,
        'convex_delegations': False,
        'convex_snapshot_curve': False,
        
        # StakeDAO
        'stakedao_delegations': False,
        'stakedao_staked_sdcrv': False,
        'stakedao_locker': False,
        'stakedao_snapshot_curve': False,

        #Votium
        'votium_bounties_v2': False,
        'votium_bounties_v1': False,

        # Warden
        'warden_vesdt_boost_delegation': False,
    }
    placeholder_list = []
    for key in manager_config.keys():
        placeholder_list.append({ 'component_name': key,'run_component': False})
   
    if form.validate_on_submit():
        load_initial= form.load_initial.data if form.load_initial.data else False
        should_fetch = form.should_fetch.data if form.should_fetch.data else False
        load_cutoff  = form.load_cutoff.data if form.load_cutoff.data else False
        # config = form.manager_config.data if form.manager_config.data else placeholder_list
        mc = {}
        config = []
        i = 0
        for entry in form.manager_config.data:
            mc[placeholder_list[i]['component_name']] = entry['run_component'] 
            config.append({'component_name': placeholder_list[i]['component_name'], 'run_component': entry['run_component']})
            i += 1
        manager = Manager(
            mc, 
            should_fetch, 
            load_initial,
            # Liquidity Specific
            load_cutoff,
            )
        manager.manage()
    else:
        load_initial = False
        should_fetch = False
        load_cutoff = False
        config = placeholder_list

    form.process(data={
        'load_initial': load_initial, 
        'should_fetch':should_fetch, 
        'load_cutoff': load_cutoff, 
        'manager_config':config,
        })
    

    file_info = generate_file_info()
    return render_template(
        'data_manager.jinja2',
        title='The Center For Llamas who want to Curve good',
        subtitle='and learn to do governance stuff good too.',
        template='home-template',
        form=form,
        file_info = file_info
    )




def generate_file_info(is_alt_path=False):
    filename_list = [
        'gauge_to_lp_map',
        'curve_locker',
        'curve_gauge_votes',
        'curve_liquidity_v2',
        'curve_liquidity_cutoff_v2',
        # Convex Data
        'convex_delegations',
        'convex_locker',
        'convex_snapshot_votes',
        'convex_snapshot_votes_origin',
        # StakeDao Data
        'stakedao_delegations',
        'stakedao_staked_sdcrv',
        'stakedao_locker',
        'stakedao_snapshot_votes',
        'stakedao_snapshot_votes_origin',
        # Votium
        'votium_v2',
        'votium_v1',
        # Warden
        'warden_vesdt_boost_delegation',
        ]
    file_info = {}
    now_time = dt.now()
    found_count = 0
    for file in filename_list:
        file_info[file] = {'last_modified': None, 'days': -1}
        for path in ['raw_data']:
            try:
                if is_alt_path:
                    prefix = 'center-for-llamas/'
                else:
                    prefix = ''
                date = dt.fromtimestamp(os.path.getmtime(f"{prefix}app/data/{path}/{file}.csv"))
                file_info[file]['last_modified'] = date
                file_info[file]['days'] = (now_time - date).days

                print(f"{date}\t\t{file}")
            except:
                print(f"\t\tno file found for {file}")
    if found_count == 0 and not is_alt_path:
        return generate_file_info(True)
    return file_info