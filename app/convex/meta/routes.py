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

from app.utilities.utility import pd, np

from app.curve.gauges.routes import get_approved
from app.utilities.utility import get_now, get_plotly_failed_chart, format_plotly_figure
from .models import ConvexUnlocks

# Blueprint Configuration
convex_meta_bp = Blueprint(
    'convex_meta_bp', __name__,
    url_prefix='/convex/meta',
    template_folder='templates',
    static_folder='static'
)


@convex_meta_bp.route('/unlocks', methods=['GET'])
def unlocks():
    df_convex_locker_user_epoch = app.config['df_convex_locker_user_epoch']
    convex_unlocks = ConvexUnlocks(df_convex_locker_user_epoch)
    df_unlocks = convex_unlocks.df_unlocks
    # df_unlocks = df_unlocks.replace(np.nan, None)
    df_unlocks = df_unlocks.sort_values(['next_unlock', 'current_locked'], ascending=False)
    df_local = df_unlocks.head(20)

    # Build chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        title=f"Top 20 Upcoming Unlocks {df_local.iloc[0].epoch_end}",
            xaxis_title="User",
            yaxis_title="vlCVX Up For Exiting",
            yaxis2_title="Relative Share of Position",
            height=600,
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
            x=df_local.display_name,
            y=df_local.next_unlock,
            name="Next Unlock",
            # color="pool_name"
        ),
        secondary_y=False
    )

    fig = fig.add_trace(
        go.Scatter(
            x = df_local.display_name,
            y = df_local.next_unlock / df_local.current_locked, 
            name = "Position %",
            line_shape='hvh',
            # line_width=3,
        ),
        secondary_y=True
    )

    # fig.add_vline(x=get_now(), line_width=3, line_dash="dash", line_color="black", )

    fig.update_layout(autotypenumbers='convert types')
    fig.update_yaxes(rangemode="tozero")

    # Build Plotly object
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'convex_unlocks.jinja2',
        title='Convex Meta: Unlocks',
        template='curve-meta-show',
        body="",
       
        df_head = df_unlocks,
        graphJSON = graphJSON,

    )
