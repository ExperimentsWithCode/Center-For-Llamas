import markdown

nerd_stuff =markdown.markdown(
'''
# Architecture
Flask based website powered by Pandas Dataframes following a Model View Controler structure. An ode to oldschool microframeworks. 

## Model
Each folder has `models.py` which reads data from a CSV and forms dataframes of data.

**there is no database at present and csv fed dataframes seems to be plenty effective for the time being**

### Data
* At present, data is queried from API's and stored as CSVs. 
* Data is loaded by processor which takes raw data and parses it into desired tables and formats, stored as CSVs.
* The server reads the CSV's and formats columns defined in each `models.py`

This three step process helps by:

* Reducing load times when starting up server (especially relevant when less frequent site visits)
* Allows for faster development as no need to wait for processing each change.
    * Allows more nuance in where in lifecycle of data to address issues.
* Reduces unintended changes vs prior jupyter setup by enshrining queries into a `fetch.py` files.
* Generate more meta tables which don't significantly affect load times to produce more enriched data.
 
## View
Each folder has a `/templates` folder which contains jinja2 template files which are hybrid html/python files. 
These define how to display information.

## Controller
Each folder has `routes.py` which defines individual pages and any data handling between data source and the display. 
Here we define what info populates charts, tables, etc

## Content 
Easily convert markdown to HTML for larger text passages to avoid dealing with HTML formatting

## Mix and match
Each model can use other models as building blocks. Allowing each additional component to build off previous ones.

The dream would be for anyone to contribute novel components and share them with others to add to their local package or get merged up into the master.

A way to enable composable collaborative data science!
___

# Enjoyable Dev Expirience
Can pull the repo, query data and it just runs. No setting up databases. No dealing with crazy JS files. 
This is nearly 100% python. 
                  
The architecture lets you pull data and explore what you find interesting about it right in jupyter. 

Once an interesting view is found via plotly charts, just copy it into that components routes page and add the figure to temmplate.

Flask automatically recognizes saves so running locally can get charts up from a notebook to UI view rather quickly.

I'm using grid.js to manage the tables which handles pagination, searching, and sorting with minimal effort. Even handles multiple sort options (using shift).

___
# Reference Links

* Data mostly from [Flipside](https://www.flipsidecrypto.xyz/)
    * Now merging with [Snapshot Api](https://docs.snapshot.org/tools/api)
        * Which interestly enough you can query through flipsides API from their indexed records or snapshot directly


* Currently using Boostrap Themes. 
    * Current theme: [Minty](https://bootswatch.com/minty/)

* Tables are reliant on a Javascript library [Grid.js](https://gridjs.io/docs/examples/server-side-sort)
    * Eventually should make server side sorting
    * Though now local sorting is working

* Charts are reliant on [Flask-Plotly](https://github.com/alanjones2/Flask-Plotly)
    * [example](https://github.com/alanjones2/Flask-Plotly/blob/main/plotly/app2.py)

* URL structure is managed by [Flask Blueprints](https://flask.palletsprojects.com/en/1.1.x/blueprints/) 

''',
extensions=["fenced_code"]
)