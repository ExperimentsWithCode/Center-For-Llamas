from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_login import LoginManager
from flask_redis import FlaskRedis
import traceback
from flask_wtf.csrf import CSRFProtect

from flask_basicauth import BasicAuth

try:
    from config import use_local_files
except:
    use_local_files = True

RAW_FOLDER_PATH = 'raw_data'
UPLOADED_FOLDER_PATH = 'imported_processed'
if use_local_files:
    MODELS_FOLDER_PATH = 'processed'
else:
    MODELS_FOLDER_PATH = UPLOADED_FOLDER_PATH



try:
    from config import basic_auth_username, basic_auth_password
except:
    basic_auth_username = 'admin'
    basic_auth_password = 'YouWouldntUseTheDefaultPasswordWouldYou'

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = basic_auth_username
app.config['BASIC_AUTH_PASSWORD'] = basic_auth_password


basic_auth = BasicAuth(app)
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
csrf = CSRFProtect()

def init_app():
    """Initialize the core application."""
    
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.DevConfig')
    app.app_context()
    
    # app.config['WTF_CSRF_TIME_LIMIT'] = 20* 60
    # Initialize Plugins
    # db.init_app(app)
    r.init_app(app)
    csrf.init_app(app)
    basic_auth = BasicAuth(app)

    # migrate.init_app(app, db)
    # login_manager.init_app(app)

    with app.app_context():
        # Include local applications routing
        try:
            from .home.routes import home_bp
            from .curve.gauges.routes import gauges_bp

            from .curve.locker.routes import curve_locker_vecrv_bp
            from .curve.gauge_votes.routes import gauge_votes_bp
            from .curve.gauge_checkpoints.routes import gauge_checkpoints_bp

            from .curve.liquidity.routes import curve_liquidity_bp



            from .convex.snapshot.routes import convex_snapshot_bp
            from .convex.locker.routes import convex_vote_locker_bp

            from .convex.votium_bounties.routes import votium_bounties_bp
            from .convex.votium_bounties_v2.routes import votium_bounties_v2_bp

            from .convex.delegations.routes import convex_snapshot_delegations_bp

            from .stakedao.snapshot.routes import stakedao_snapshot_bp
            from .stakedao.staked_sdcrv.routes import stakedao_staked_sdcrv_bp
            from .stakedao.locker.routes import stakedao_locked_vesdt_bp

            from .stakedao.delegations.routes import stakedao_snapshot_delegations_bp

            from .address_book.routes import address_book_bp
            from .data.interface.routes import data_bp
            
            # Meta Dependencies
            from .curve.meta.routes import curve_meta_bp



        

        # Register Blueprints
            app.register_blueprint(home_bp)
            app.register_blueprint(gauges_bp, url_prefix='/curve/gauges')
            app.register_blueprint(curve_locker_vecrv_bp, url_prefix='/curve/locker')
            app.register_blueprint(gauge_votes_bp, url_prefix='/curve/gauge_votes')
            app.register_blueprint(gauge_checkpoints_bp, url_prefix='/curve/checkpoints')

            app.register_blueprint(curve_liquidity_bp, url_prefix='/curve/liquidity')

            app.register_blueprint(convex_snapshot_bp, url_prefix='/convex/snapshot')
            app.register_blueprint(convex_vote_locker_bp, url_prefix='/convex/vote_locker')
            app.register_blueprint(convex_snapshot_delegations_bp, url_prefix='/convex/delegations')

            app.register_blueprint(votium_bounties_bp, url_prefix='/convex/votium')
            app.register_blueprint(votium_bounties_v2_bp, url_prefix='/convex/votium_v2')

            app.register_blueprint(stakedao_snapshot_bp, url_prefix='/stakedao/snapshot')
            app.register_blueprint(stakedao_staked_sdcrv_bp, url_prefix='/stakedao/staked_sdcrv')
            app.register_blueprint(stakedao_locked_vesdt_bp, url_prefix='/stakedao/locker')
            app.register_blueprint(stakedao_snapshot_delegations_bp, url_prefix='/stakedao/delegations')

            app.register_blueprint(address_book_bp, url_prefix='/directory')
            app.register_blueprint(curve_meta_bp, url_prefix='/curve/meta')

            app.register_blueprint(data_bp, url_prefix='/data')

        except Exception as e:
            # Only load necessary blueprints to load site and upload data
            print(e)
            print(traceback.format_exc())
            # this allows us to load data from the website directly
            from .home.routes import home_bp
            from .data.interface.routes import data_bp

            app.register_blueprint(home_bp)
            app.register_blueprint(data_bp, url_prefix='/data')



        # # Create Database Models
        # db.create_all()

        # Compile static assets
        # compile_static_assets(assets)  # Execute logic
        
        return app
