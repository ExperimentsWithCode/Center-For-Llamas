from flask import current_app as app
from flask import Blueprint, render_template, redirect, url_for
# from flask_login import current_user, login_required

from flask import Response
from flask import request

from datetime import datetime
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go

from .forms.power_diff_form import PowerDiffForm
from .forms.contributing_factors_form import ContributingFactorsForm
from app.curve.gauges.routes import get_approved

from .models import get_meta, ProcessContributingFactors

# Blueprint Configuration
curve_meta_bp = Blueprint(
    'curve_meta_bp', __name__,
    url_prefix='/curve/meta',
    template_folder='templates',
    static_folder='static'
)


@curve_meta_bp.route('/', methods=['GET'])
def index():
    form = PowerDiffForm()

    this_round=0
    top_x = 20 
    compare_round=2

    df_head, df_tail = get_meta(this_round, top_x, compare_round)

    # Build chart
    fig = px.bar(df_head,
                        x=df_head.display_name,
                        y=df_head.power_difference,
                        # color=df_formated_shorts['name'],
                    title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_head.iloc[0]['checkpoint_timestamp']}",
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
                    title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_tail.iloc[0]['checkpoint_timestamp']}",
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
    form = PowerDiffForm()
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
                    title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_head.iloc[0]['checkpoint_timestamp']}",
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
                    title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_tail.iloc[0]['checkpoint_timestamp']}",
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


@curve_meta_bp.route('/contributing_factors', methods=['GET', 'POST'])
def contributing_factors():
    df_approved_gauges = get_approved()

    form = ContributingFactorsForm()
    if form.validate_on_submit():
        target_gauge= form.target_gauge.data if form.target_gauge.data else None
        compare_back = form.compare_back.data if form.compare_back.data else 16
    else:
        target_gauge=None
        compare_back=16
    form.process(data={'target_gauge': target_gauge, 
                       'compare_back':compare_back, 
                       })
    if not target_gauge:
        return render_template(
            'contributing_factors.jinja2',
            title='Curve Meta: Contributing Factors',
            template='contributing_factors',
            body="",
            form=form,
            df_approved_gauges = df_approved_gauges
            )
    
    pcf = ProcessContributingFactors()
    df = pcf.process_all(target_gauge, compare_back)

    if len(df) == 0:
        return render_template(
            'contributing_factors.jinja2',
            title='Curve Meta: Contributing Factors',
            template='contributing_factors',
            body="Gauge not found",
            form=form,
            df_approved_gauges = df_approved_gauges
            )
    
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'] == target_gauge]

    # Build chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df.checkpoint_timestamp,
        y=df.total_bounty_value,
        name="Bounty Value"
    ))


    fig.add_trace(go.Bar(
        x=df.checkpoint_timestamp,
        y=df.issuance_value,
        name="Issuance Value",
        # yaxis="y2"
    ))

    fig.add_trace(go.Scatter(
        x=df.checkpoint_timestamp,
        y=df.avg_crv_price,
        name="Avg CRV Price",
        yaxis="y2"
    ))

    fig.add_trace(go.Scatter(
        x=df.checkpoint_timestamp,
        y=df.total_vote_percent,
        name="veCRV Vote Percent",
        yaxis="y3"
    ))

    fig.add_trace(go.Scatter(
        x=df.checkpoint_timestamp,
        y=df.total_balance_usd,
        name="Pool Balance",
        yaxis="y4"
    ))


    # Create axis objects
    fig.update_layout(
        xaxis=dict(
            domain=[0.1, 0.9]
        ),
        yaxis=dict(
            title="Bounty or Issuance Value (USD)",
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            )
        ),
        yaxis2=dict(
            title="Avg. CRV Price (USD)",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.01
        ),
        yaxis3=dict(
            title="Total veCRV Vote Percent",
            titlefont=dict(
                color="#9467bd"
            ),
            tickfont=dict(
                color="#9467bd"
            ),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        yaxis4=dict(
            title="Pool Balance (USD)",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.99
        )
    )

    # Update layout properties
    fig.update_layout(
        title_text=f"Curve Incentives: {df.iloc[0]['gauge_symbol']}",
        height=600,
    )
    fig.update_yaxes(rangemode="tozero")

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Build chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df.votium_round,
        y=df.total_bounty_value,
        name="Bounty Value"
    ))


    fig.add_trace(go.Bar(
        x=df.votium_round,
        y=df.issuance_value,
        name="Issuance Value",
        # yaxis="y2"
    ))

    fig.add_trace(go.Box(
        x=df.votium_round,
        y=df.avg_crv_price,
        name="Avg CRV Price",
        yaxis="y2"
    ))

    fig.add_trace(go.Scatter(
        x=df.votium_round,
        y=df.total_vote_percent,
        name="veCRV Vote Percent",
        yaxis="y3"
    ))

    fig.add_trace(go.Box(
        x=df.votium_round,
        y=df.total_balance_usd,
        name="Pool Balance",
        yaxis="y4"
    ))


    # Create axis objects
    fig.update_layout(
        xaxis=dict(
            domain=[0.1, 0.9]
        ),
        yaxis=dict(
            title="Bounty or Issuance Value (USD)",
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            )
        ),
        yaxis2=dict(
            title="Avg. CRV Price (USD)",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.01
        ),
        yaxis3=dict(
            title="Total veCRV Vote Percent",
            titlefont=dict(
                color="#9467bd"
            ),
            tickfont=dict(
                color="#9467bd"
            ),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        yaxis4=dict(
            title="Pool Balance (USD)",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            anchor="free",
            overlaying="y",
            side="right",
            position=0.99
        )
    )
    fig.update_layout(
        title_text=f"Curve Incentives: {df.iloc[0]['gauge_symbol']}",
        height=600,
    )
    fig.update_yaxes(rangemode="tozero")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')

    # Build Plotly object
    graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'contributing_factors.jinja2',
        title='Curve Meta: Contributing Factors',
        template='curve-meta-show',
        body="",

        form=form,
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        graphJSON = graphJSON,
        graphJSON2 = graphJSON2,
        df = df,
        df_approved_gauges = df_approved_gauges

    )


# @curve_meta_bp.route('/projections/', methods=['POST'])
# def projections():
#     form = PowerDiffForm()
#     if form.validate_on_submit():
#         this_round= form.main_round.data if form.main_round.data else 0
#         top_x = form.top_results.data
#         compare_round= form.compare_round.data
#     else:
#         this_round=0
#         top_x = 20 
#         compare_round=1
#     df_head, df_tail = get_meta(this_round, top_x, compare_round)

#     # Build chart
#     fig = px.bar(df_head,
#                         x=df_head.display_name,
#                         y=df_head.power_difference,
#                         # color=df_formated_shorts['name'],
#                     title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_head.iloc[0]['checkpoint_timestamp']}",
#                     # line_shape='hvh'
#                     height=600
#                     )
#     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
#     fig.update_layout(autotypenumbers='convert types')

#     # Build Plotly object
#     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#     # Build chart
#     fig = px.bar(df_tail,
#                         x=df_tail.display_name,
#                         y=df_tail.power_difference,
#                         # color=df_formated_shorts['name'],
#                     title=f"Power Difference: Leader Board, Round: -{this_round}, Date: {df_tail.iloc[0]['checkpoint_timestamp']}",
#                     # line_shape='hvh'
#                     height=600
#                     )
#     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
#     fig.update_layout(autotypenumbers='convert types')

#     # Build Plotly object
#     graphJSON2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


#     return render_template(
#         'projections.jinja2',
#         title='Curve Gauge Projections',
#         template='curve-meta-show',
#         body="",

#         form=form,
        
#         df_head = df_head,
#         df_tail = df_tail,
#         graphJSON = graphJSON,
#         graphJSON2 = graphJSON2,
#         this_round = this_round,
#         top_x = top_x, 
#         compare_round = compare_round
#     )