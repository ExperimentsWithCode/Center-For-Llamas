### Welcome to the repo for 
# The Center for Llamas who want to Curve good
## and do governance stuff good too
___
# To run
In the root directory enter the following in your terminal.
```bash
python wsgi.py
```
___
# Overview
Curve has a complex governance ecosystem. 

CRV holders lock in the locker to vote on Gauge Votes on chain (among other things).

Some CRV is locked in a wrapper contract such as Convex's cvxCRV and delegates its votes to vlCVX votes via snapshot. 

This dashboard hopes to clearly present the activity of Curve Governance and expand into its various wrapped markets to complete the picture. 

___
# To Do
### Data
[X] Map Gauge to Pool to Name to Symbol

[] Snapshot votes prior to December 22 arrive in a distinct format.
* Need to update to resolve:
    - Choices: [x, y, z]
    - Vote_Option: [x, y, z]
    
* Currently handles Vote_Option as dict.

* Flipside will not be retroactively updating this so need to pull prior data from Snapshot via rate limited process.

* Flipside will not be correct this
    
    [] Pursue data from snapshot graphql

### Views

[X] Build out Snapshot Show page for specific views.

[X] Build out Votium Bounty index/show

[] Build out StakeDAO sdCRV index/show

[] Build out StakeDAO Bounty index/show


[] Build out meta aggregation of all above. 

### Bug fixes

[] Fix CRV Locked Chart bar chart to include withdraw and deposit info.

[] Fix Gauge Votes bar chart its not right for some reason.




___
# Points of Frustration
* Convex doesn't have a registry of what gauge addresses their vote choices actually vote to.
    * Convex uses swap address (sometimes token) instead of gauge address, so need matching, but helpful for future alt tracking liquidity. 

    * it is hard to search an address by prefix.
    * to this effort I have:
        * queried all factory deployed pools
        * harvested the main contracts
        * queried all v2 deployed pools
    * I have matched 113 / 122 gauges to convex choices
        * 9 remaining. 
        * several are cross chain, not ins cope. Many are USDC pairs and v2's.
    * Some votes do not 
* Some curve tokens are just random contracts deployed by random EOAs like Frax USDC. 
    * This
___
# Architecture
Flask based website powered by Pandas Dataframes following a Model View Controler structure. 
## Model
Each folder has `models.py` which reads data from a CSV and forms dataframes of data.

**there is no database at present and csv fed dataframes seems to be plenty effective for the time being**

## View
Each folder has a `/templates` folder which contains jinja2 template files which are hybrid html/python files. 
These define how to display information.

## Controller
Each folder has `routes.py` which defines individual pages and any data handling between data source and the display. 
Here we define what info populates charts, tables, etc

The core application is defined in `__init__.py` in the `/app` folder

## Data
At present data is simply CSV's a title appendage. 

There is a jupyter notebook `load_data.ipynb` which taps calls **Flipside** by API to update these data sources. 

To apply changes restart the server to precompile new dataframes. 

### app.config
A lot of data references each other. Rather than having each server refresh rebuild each model multiple times every time its referenced, models are stored in the `app.config`. 

**However this can only work in the application context.**

In order for the models to work locally in jupyter notebooks we import dataframes under a try except statement, first through the `app.config` and if that fails (it's running locally), import directly which will take more time as each model builds its own dependencies. 

```python
try:
    dataframe_model = app.config['dataframe_model']
except: 
    from app.protocol.component.models import dataframe_model
```
Likewise for storing data into the `app.config` wrap that in a try except, and use a print statement to ensure we can tell that's not storing properly in web context.
```python
try
    app.config['dataframe_model'] = dataframe_model
except:
    print(f"could not register in app.config\n\t{component}")
```
___
# General Dev Flow
1. create component folder
2. create `models.py`
3. create flipside query
4. create local dataframe in `models.py` which generates all desired views
5. create `routes.py`
6. assemble out the info for each view
7. create `templates` 
8. create a jinja2 template for each view.
9. update `__init__.py` 
* to import blueprint from `routes.py`
* to register the new blueprint  
___
# Reference Links
* Currently using Boostrap Themes. 
    * Current theme: https://bootswatch.com/minty/

* Tables are reliant on a Javascript library Grid.js
    * Eventually should make server side sorting
    * https://gridjs.io/docs/examples/server-side-sort

* Charts are reliant on Flask-Plotly
    * https://github.com/alanjones2/Flask-Plotly
        * example
        * https://github.com/alanjones2/Flask-Plotly/blob/main/plotly/app2.py

* URL structure is managed by Flask Blueprints
    * https://flask.palletsprojects.com/en/1.1.x/blueprints/