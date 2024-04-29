from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for, make_response, jsonify
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from werkzeug.utils import secure_filename
import os


from app.data.reference import core_filename_list
from app.utilities.utility import pd, get_now, dt, print_mode
from app.data.local_storage import save_file, cwd

from .forms import DataManagerForm

from ..data_manager import Manager

from app import basic_auth, csrf

# from app.curve.gauges.routes import get_approved
# from app.utilities.utility import get_now

# Blueprint Configuration
data_bp = Blueprint(
    'data_bp', __name__,
    url_prefix='/data',
    template_folder='templates',
    static_folder='static'
)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@csrf.exempt
@basic_auth.required
@data_bp.route('/orange_mocha_frappacino/', methods=['POST'])
def upload_file():
    """
    Need to add way to verify filenames.
        For now lazy and just accept. If filenames match, good. 
        uploading from same repo so should be aligned in filenames
        but won't provide error if local is ahead on filename. 
        So should still add verification here. 
    """
    if not request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_file(file, file.filename)
        return jsonify(success=True)
    
    return jsonify(success=False)
    
@basic_auth.required
@data_bp.route('/csv/<string:filename>/', methods=['GET'])  
def download_file(filename):
    """
    Add error if file does not exist.
    """
    csv_file = f"{cwd}/app/data/processed/{filename}.csv"

    try:
        date = dt.fromtimestamp(csv_file)
        (get_now() - date).days
    except:
        print_mode("False")
        return jsonify(success=False)

    with open(csv_file) as fp:
        csv = fp.read()
        return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-disposition":
                    f"attachment; filename={filename}.csv"})

    # csv_file = f"{cwd}/app/data/processed/{filename}.csv"
    # # csv = 'foo,bar,baz\nhai,bai,crai\n'  
    # if not os.path.getmtime(csv_file):
    #     return jsonify(success=False)
    # response = make_response(csv_file)
    # cd = f"attachment; filename={filename}.csv"
    # response.headers['Content-Disposition'] = cd 
    # response.mimetype='text/csv'
    # return response

# def getPlotCSV():
#     csv_file = f"{cwd}/app/data/processed/{filename}.csv"






@data_bp.route('/male_models', methods=['GET','POST'])
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
        'convex_snapshot_curve': False,
        'convex_locker': False,
        'convex_delegations': False,

        # StakeDAO
        'stakedao_snapshot_curve': False,
        'stakedao_staked_sdcrv': False,
        'stakedao_locker': False,
        'stakedao_delegations': False,


        #Votium
        'votium_bounties_v2': False,
        'votium_bounties_v1': False,

        # Warden
        'warden_vesdt_boost_delegation': False,

        # Address Book
        'address_book_actors': False,
    }
    placeholder_list = []
    for key in manager_config.keys():
        placeholder_list.append({ 'component_name': key,'run_component': False})
   
    if form.validate_on_submit():
        load_initial= form.load_initial.data if form.load_initial.data else False
        should_fetch = form.should_fetch.data if form.should_fetch.data else False
        should_process = form.should_process.data if form.should_process.data else False
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
            should_process,
            load_initial,
            # Liquidity Specific
            load_cutoff,
            )
        manager.manage()
    else:
        load_initial = False
        should_fetch = False
        should_process = False
        load_cutoff = False
        config = placeholder_list

    form.process(data={
        'load_initial': load_initial, 
        'should_fetch':should_fetch, 
        'should_process':should_process, 

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
    file_info = {}
    now_time = get_now()
    found_count = 0
    for file in core_filename_list:
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

                found_count+=1
            except:
                pass
                # print(f"\t\tno file found for {file}")
    if found_count == 0 and not is_alt_path:
        return generate_file_info(True)
    return file_info