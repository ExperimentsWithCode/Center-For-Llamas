

try:
    from flask import current_app as app
    df_gauge_rounds_all_by_user = app.config['df_gauge_rounds_all_by_user']
    df_convex_snapshot_vote_choice = app.config['df_convex_snapshot_vote_choice']
    df_votium_bounty_formatted = app.config['df_votium_bounty_formatted']
except:
    from app.curve.gauges import df_gauge_rounds_all_by_user
    from app.convex.snapshot import df_convex_snapshot_vote_choice
    from app.convex.votium_bounties import df_votium_bounty_formatted