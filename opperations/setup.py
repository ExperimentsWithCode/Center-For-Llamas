import sys
import pandas as pd
from IPython import get_ipython


"""
Pathing
"""

ipython = get_ipython()

# Find performance bottlenecks by timing Python cell execution
# ipython.magic("load_ext autotime") # ipython.magic("...") is equivalent to % in Jupyter cell

# Reload all modules (except those excluded by %aimport) every time before executing the Python code typed
# See https://ipython.org/ipython-doc/stable/config/extensions/autoreload.html
# ipython.magic("load_ext autoreload")
# ipython.magic("autoreload 2")

# Append the root directory to Python path,
# this allows you to store notebooks in `experiments/notebooks/` sub-directory and access model Python modules
sys.path.append("..")
# sys.path.append("../../..")

# Configure Pandas to raise for chained assignment, rather than warn, so that we can fix the issue!
pd.options.mode.chained_assignment = 'raise'

# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"


# """
# Local App context
# """
# from flask import Flask
# from config import flipside_api_key, DevConfig
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# db = SQLAlchemy()
# migrate = Migrate()



# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(DevConfig)

#     db.init_app(app)
#     migrate.init_app(app, db)

#     with app.app_context():
#         from app.core.user_address.models import Address
#         from app.core.known_collectively_name.models import KnownAs
#         from app.core.contract_address.models import ContractAddress
#         from app.core.tokens.models import TokenContract

#         from app.curve.components.gauge_factories.models import CurveGaugeFactoryContract
#         from app.curve.components.pools.models import CurvePoolContract
#         from app.curve.components.gauges.models import GaugeContract

#         from app.curve.gauges.approved_gauges.models import ApprovedGauge
#         from app.curve.gauges.deployers.models import DeployedGauge
#         from app.curve.gauges.gauge_types.models import GaugeType
#         from app.curve.gauges.gauge_type_weights.models import GaugeTypeWeight 


#         db.create_all()

#     return app