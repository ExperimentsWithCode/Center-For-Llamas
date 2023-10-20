from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px

from .forms import MetaForm

from .models import get_meta

# Blueprint Configuration
curve_meta_bp = Blueprint(
    'curve_meta_bp', __name__,
    url_prefix='/curve/meta',
    template_folder='templates',
    static_folder='static'
)


@curve_meta_bp.route('/', methods=['GET'])
def index():
    form = MetaForm()

    this_round=0
    top_x = 20 
    compare_round=2

    df_head, df_tail = get_meta(this_round, top_x, compare_round)

    # Build chart
    fig = px.bar(df_head,
                        x=df_head.display_name,
                        y=df_head.power_difference,
                        # color=df_formated_shorts['name'],
                    title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_head.iloc[0]['period_end_date']}",
                    # line_shape='hvh'
                    height=600
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Build chart
    fig = px.bar(df_tail,
                        x=df_tail.display_name,
                        y=df_tail.power_difference,
                        # color=df_formated_shorts['name'],
                    title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_tail.iloc[0]['period_end_date']}",
                    # line_shape='hvh'
                    height=600
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'index_curve_meta.jinja2',
        title='Curve Meta',
        template='curve-meta-show',
        body="",

        form=form,
        
        df_head = df_head,
        df_tail = df_tail,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        this_round = this_round,
        top_x = top_x, 
        compare_round = compare_round
    )


@curve_meta_bp.route('/', methods=['POST'])
def custom_index():
    form = MetaForm()
    if form.validate_on_submit():
        this_round= form.main_round.data if form.main_round.data else 0
        top_x = form.top_results.data
        compare_round= form.compare_round.data
    else:
        this_round=0
        top_x = 20 
        compare_round=1

    df_head, df_tail = get_meta(this_round, top_x, compare_round)

    # Build chart
    fig = px.bar(df_head,
                        x=df_head.display_name,
                        y=df_head.power_difference,
                        # color=df_formated_shorts['name'],
                    title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_head.iloc[0]['period_end_date']}",
                    # line_shape='hvh'
                    height=600
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Build chart
    fig = px.bar(df_tail,
                        x=df_tail.display_name,
                        y=df_tail.power_difference,
                        # color=df_formated_shorts['name'],
                    title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_tail.iloc[0]['period_end_date']}",
                    # line_shape='hvh'
                    height=600
                    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'index_curve_meta.jinja2',
        title='Curve Meta',
        template='curve-meta-show',
        body="",

        form=form,
        
        df_head = df_head,
        df_tail = df_tail,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        this_round = this_round,
        top_x = top_x, 
        compare_round = compare_round
    )