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
from plotly.subplots import make_subplots

from app.utilities.utility import pd
from .forms.power_diff_form import PowerDiffForm
from .forms.contributing_factors_form import ContributingFactorsForm, ContributingFactorsCompareForm
from app.curve.gauges.routes import get_approved
from app.utilities.utility import get_now
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

    graph_list = get_contributing_factors_graphs(df)

    return render_template(
        'contributing_factors.jinja2',
        title='Curve Meta: Contributing Factors',
        template='curve-meta-show',
        body="",

        form=form,
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        graph_list = graph_list,
        df = df,
        df_approved_gauges = df_approved_gauges

    )

@curve_meta_bp.route('/contributing_factors/<string:gauge_addr>', methods=['GET'])
def contributing_factors_show(gauge_addr):
    df_approved_gauges = get_approved()
    target_gauge = gauge_addr
    compare_back = 16
    
    form = ContributingFactorsForm()
    form.process(data={'target_gauge': target_gauge, 
                       'compare_back':compare_back, 
                       })
    
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

    graph_list = get_contributing_factors_graphs(df)

    return render_template(
        'contributing_factors.jinja2',
        title='Curve Meta: Contributing Factors',
        template='curve-meta-show',
        body="",

        form=form,
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        graph_list = graph_list,
        df = df,
        df_approved_gauges = df_approved_gauges

    )

@curve_meta_bp.route('/contributing_factors/compare', methods=['GET', 'POST'])
def contributing_factors_compare():
    df_approved_gauges = get_approved()

    form = ContributingFactorsCompareForm()
    if form.validate_on_submit():
        target_gauges= form.target_gauges.data if form.target_gauges.data else None
        compare_back = form.compare_back.data if form.compare_back.data else 16
        target_gauges = format_input_to_list(target_gauges)

    else:
        target_gauges=None
        compare_back=16
    form.process(data={'target_gauges': target_gauges, 
                       'compare_back':compare_back, 
                       })
    if not target_gauges:
        return render_template(
            'contributing_factors_compare.jinja2',
            title='Curve Meta: Contributing Factors',
            template='contributing_factors',
            body="",
            form=form,
            df_approved_gauges = df_approved_gauges
            )
    
    pcf = ProcessContributingFactors()
    df = pcf.process_all(target_gauges, compare_back)

    if len(df) == 0:
        return render_template(
            'contributing_factors_compare.jinja2',
            title='Curve Meta: Contributing Factors',
            template='contributing_factors',
            body="Gauge not found",
            form=form,
            df_approved_gauges = df_approved_gauges
            )
    
    df_curve_gauge_registry = app.config['df_curve_gauge_registry']
    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'].isin(target_gauges)]

    graph_list = generate_plot_per_gauge(df)

    return render_template(
        'contributing_factors_compare.jinja2',
        title='Curve Meta: Contributing Factors Compare',
        template='curve-meta-compare-show',
        body="",

        form=form,
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        graph_list = graph_list,
        df = df,
        df_approved_gauges = df_approved_gauges

    )

@curve_meta_bp.route('/contributing_factors/voter/<string:target_voter>', methods=['GET'])
def contributing_factors_voter(target_voter):
    df_approved_gauges = get_approved()
    target_gauges = []
    df_convex_snapshot_vote_choice = get_snapshot_votes_back(app.config['df_convex_snapshot_vote_choice'], target_voter, 16)
    df_stakedao_snapshot_vote_choice = get_snapshot_votes_back(app.config['df_stakedao_snapshot_vote_choice'], target_voter, 16)
    df_curve_votes_back = get_vecrv_votes_back(app.config['df_checkpoints'], target_voter, 16)

    convex_gauge_votes = list(df_convex_snapshot_vote_choice.gauge_addr.unique())
    stakedao_gauge_votes = list(df_stakedao_snapshot_vote_choice.gauge_addr.unique())
    curve_gauge_votes = list(df_curve_votes_back.gauge_addr.unique())
    target_gauges = list(set(convex_gauge_votes + stakedao_gauge_votes + curve_gauge_votes))
    compare_back = 16

    form = ContributingFactorsCompareForm()
    form.process(data={'target_gauges': target_gauges, 
                       'compare_back':compare_back, 
                       })
    if not target_gauges:
        return render_template(
            'contributing_factors.jinja2',
            title='Curve Meta: Contributing Factors',
            template='contributing_factors',
            body="",
            form=form,
            df_approved_gauges = df_approved_gauges
            )
    
    pcf = ProcessContributingFactors()
    df = pcf.process_all(target_gauges, compare_back)

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
    local_df_curve_gauge_registry = df_curve_gauge_registry[df_curve_gauge_registry['gauge_addr'].isin(target_gauges)]

    graph_list = generate_plot_per_gauge(df)

    return render_template(
        'contributing_factors_compare.jinja2',
        title='Curve Meta: Contributing Factors Compare',
        template='curve-meta-compare-show',
        body="",

        form=form,
        local_df_curve_gauge_registry = local_df_curve_gauge_registry,
        graph_list = graph_list,
        df = df,
        df_approved_gauges = df_approved_gauges

    )


def format_input_to_list(raw_value):
    x = raw_value.split(',')
    new_list = []
    for item in x:
        item = item.strip()
        removal_list = ['"', "'", "\n", '[', ']', '(', ')']
        for r in removal_list:
            item = item.replace(r, '')
        item = item.strip()
        if len(item) > 0:
            new_list.append(item)
    return new_list

def get_contributing_factors_graphs(df):
    graph_list = []
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
    fig.add_vline(x=get_now(), line_width=3, line_dash="dash", line_color="black", )

    # Build Plotly object
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"Liquidity (USD), Votes (veCRV), and Yield Rate: {df.iloc[0]['gauge_symbol']} ",
            xaxis_title="Checkpoint Timestamp",
            yaxis_title="TVL (USD) or Votes (veCRV)",
            yaxis2_title="Avg Weekly Yield Rate (%)",

            # legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            # size=18,
            color="RebeccaPurple"
        ),
        # height= 1000,
    )
    fig = fig.add_trace(
        go.Bar(
            x=df.checkpoint_timestamp,
            y=df.total_balance_usd,
            name="Total Balance (USD)",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Bar(
            x=df.checkpoint_timestamp,
            y=df.total_vote_power,
            name="Total Vote Power",
            # color="pool_name"
        ),
        secondary_y=False
    )
    fig = fig.add_trace(
        go.Scatter(
            x = df.checkpoint_timestamp,
            y = df.yield_rate_adj, 
            name = "Yield Rate",
            line_shape='hvh',
            # line_width=3,
        ),
        secondary_y=True
    )
    fig.add_vline(x=get_now(), line_width=3, line_dash="dash", line_color="black", )

    fig.update_layout(autotypenumbers='convert types')
    fig.update_yaxes(rangemode="tozero")

    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    if len(df.votium_round.unique()) > 1:

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
        fig.add_vline(x=get_now(), line_width=3, line_dash="dash", line_color="black", )

        # Build Plotly object
        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    return graph_list

def generate_plot_per_gauge(df):
    graph_list = []
    df = df.sort_values(['checkpoint_id', 'total_balance_usd'], ascending=[True, False])
    fig = px.bar(
        df,
        x=df.checkpoint_timestamp,
        y=df.total_balance_usd,
        color=df.gauge_name,
        title=f"Compare: Gauge Balances (USD)",
        # line_shape='hvh'
        height=600

        )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    # fig.update_yaxes(range=[0,3], secondary_y=False)
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    fig = px.bar(
        df,
        x=df.checkpoint_timestamp,
        y=df.issuance_value,
        color=df.gauge_name,
        title=f"Compare: Gauge Issuance Value (USD)",
        # line_shape='hvh'
        height=600

        )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    # fig.update_yaxes(range=[0,3], secondary_y=False)
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    fig = px.bar(
        df,
        x=df.checkpoint_timestamp,
        y=df.total_vote_percent,
        color=df.gauge_name,
        title=f"Compare: Gauge Vote Percent",
        # line_shape='hvh'
        height=600

        )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    # fig.update_yaxes(range=[0,3], secondary_y=False)
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    fig = px.line(
        df,
        x=df.checkpoint_timestamp,
        y=df.yield_rate_adj,
        color=df.gauge_name,
        title=f"Compare: Yield Rate",
        line_shape='hvh',
        height=600

        )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    # fig.update_yaxes(range=[0,3], secondary_y=False)
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    
    local_df = df.dropna(subset = ['liquidity_usd_over_votes', 'total_balance_usd'])
    fig = px.scatter(
        local_df,
        x=local_df.checkpoint_timestamp,
        y=local_df.liquidity_usd_over_votes,
        color=local_df.gauge_name,
        size=local_df.total_balance_usd,
        title=f"Compare: Gauge Balance (USD) / Votes (veCRV) [Dot Scaled by Balance (USD)]",
        # line_shape='hvh'
        height=600

        )
    
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(autotypenumbers='convert types')
    # fig.update_yaxes(range=[0,3], secondary_y=False)
    graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    if len(df.votium_round.unique()) > 1:
        fig = px.bar(
            df,
            x=df.checkpoint_timestamp,
            y=df.total_bounty_value,
            color=df.gauge_name,
            title=f"Compare: Votium v2 Bounty Value (USD)",
            # line_shape='hvh'
            height=600

            )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_layout(autotypenumbers='convert types')
        # fig.update_yaxes(range=[0,3], secondary_y=False)
        graph_list.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    return graph_list


def get_vecrv_votes_back(df_checkpoints, taget_voter, compare_back = None):
    # df_checkpoints = app.config['df_checkpoints']
    # Filter Data
    if compare_back:
        df_checkpoints = df_checkpoints[df_checkpoints['checkpoint_id'] >= df_checkpoints.checkpoint_id.max() - compare_back]
    df_local_checkpoints = df_checkpoints[df_checkpoints['voter'] == taget_voter]
    df_local_checkpoints = df_local_checkpoints[df_local_checkpoints['weight'] > 0]
    return df_local_checkpoints


def get_snapshot_votes_back(df_vote_choice, target_voter, compare_back=None):
    if compare_back:
        df_vote_choice = df_vote_choice[df_vote_choice['checkpoint_id'] >= df_vote_choice.checkpoint_id.max()-compare_back]
    # Filter Data
    ## Votes
    ### Grab Delegated Votes if Any
    selection = [target_voter]
    mask = df_vote_choice.delegators.apply(lambda x: any(item for item in selection if item in x))
    local_df_vote_choice = df_vote_choice[mask]    
    
    local_df_vote_choice = local_df_vote_choice.sort_values(["proposal_end", 'choice_power'], axis = 0, ascending = False)
    
    ### Grab Self Votes if Any
    local_df_vote_choice_self_vote = df_vote_choice[
        df_vote_choice['voter'] == target_voter
        ]
    
    ### Concat
    df_vote_temp = local_df_vote_choice[~local_df_vote_choice['proposal_start'].isin(
        local_df_vote_choice_self_vote.proposal_start.unique()
        )]
    local_df_vote_choice = pd.concat([df_vote_temp, local_df_vote_choice_self_vote])

    return local_df_vote_choice


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