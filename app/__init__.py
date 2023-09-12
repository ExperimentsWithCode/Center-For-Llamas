from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_login import LoginManager
from flask_redis import FlaskRedis

# from config import ADDRESS, API_ETHERSCAN, ALCHEMY, API_COINGECKO, API_LIQUIDITYFOLIO

# Globally accessible libraries
# oracle_configs = {'API_ETHERSCAN': API_ETHERSCAN,
#                     'API_COINGECKO': API_COINGECKO,
#                     'API_LIQUIDITYFOLIO': API_LIQUIDITYFOLIO,
#                     'ALCHEMY': ALCHEMY,
#                     'ADDRESS': ADDRESS}
# db = SQLAlchemy()
r = FlaskRedis()
# migrate = Migrate()
# login_manager = LoginManager()

def init_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.DevConfig')
    app.app_context()
    # Initialize Plugins
    # db.init_app(app)
    r.init_app(app)
    # migrate.init_app(app, db)
    # login_manager.init_app(app)

    with app.app_context():
        # Include local applications routing
        from .home.routes import home_bp
        from .curve.gauges.routes import gauges_bp

        from .curve.locker.routes import locker_bp
        from .curve.gauge_votes.routes import gauge_votes_bp
        from .curve.gauge_rounds.routes import gauge_rounds_bp

        from .curve.liquidity.routes import curve_liquidity_bp

        from .curve.meta.routes import curve_meta_bp


        from .convex.snapshot.routes import convex_snapshot_bp
        from .convex.votium_bounties.routes import votium_bounties_bp

        from .stakedao.snapshot.routes import stakedao_snapshot_bp

    
        # from .authentication.auth.routes import auth_bp
        # from .authentication.user.routes import user_bp

        # from .snapshot.space.routes import space_bp
        # from .snapshot.proposal.routes import proposal_bp
        # from .snapshot.address.routes import address_bp
        # from .snapshot.vote.routes import vote_bp
        # from .snapshot.choice.routes import choice_bp

        # from .environment.simulator.routes import simulator_bp
        #
        # from .mechanisms.amm.routes import amm_bp
        #
        # from .interpreters.plotter.routes import plotter_bp
        #
        # from .oracles.liquidityfolio.routes import liquidityfolio_bp
        ## Including satic asset handling
            ### ???
        # from .api import routes
        # from .assets import compile_static_assets

        # Register Blueprints
        app.register_blueprint(home_bp)
        app.register_blueprint(curve_meta_bp, url_prefix='/curve/meta')

        app.register_blueprint(locker_bp, url_prefix='/curve/locker')
        app.register_blueprint(gauge_votes_bp, url_prefix='/curve/gauge_votes')
        app.register_blueprint(gauge_rounds_bp, url_prefix='/curve/gauge_rounds')

        app.register_blueprint(curve_liquidity_bp, url_prefix='/curve/liquidity')

        app.register_blueprint(convex_snapshot_bp, url_prefix='/convex/snapshot')
        app.register_blueprint(votium_bounties_bp, url_prefix='/convex/votium')

        app.register_blueprint(stakedao_snapshot_bp, url_prefix='/stakedao/snapshot'
                               )

        # app.register_blueprint(user_bp, url_prefix='/user')
        # app.register_blueprint(space_bp, url_prefix='/space')
        # app.register_blueprint(proposal_bp, url_prefix='/proposal')
        # app.register_blueprint(address_bp, url_prefix='/address')
        # app.register_blueprint(vote_bp, url_prefix='/vote')
        # app.register_blueprint(choice_bp, url_prefix='/choice')

        # app.register_blueprint(simulator_bp, url_prefix='/simulator')
        # app.register_blueprint(amm_bp, url_prefix='/amm')
        # app.register_blueprint(plotter_bp, url_prefix='/plotter')
        # app.register_blueprint(liquidityfolio_bp, url_prefix='/o/lf')

        # # Create Database Models
        # db.create_all()

        # Compile static assets
        # compile_static_assets(assets)  # Execute logic

        return app
