import markdown

to_do =markdown.markdown(
'''
# To Do

## Core Mappings
* [] Struggle to connect all gauges to their pools. 
    * Currently pulling from deployer contracts but need better way to identify all deployer contracts
    * [] Connect pool assets to Gauge for filtering
    * [] Connect lost Snapshot data which exists but cannot map from pool to gauge since no pool address linked
* [] Need to add ability to recognize if snapshot votes exist for a given pool to disable navigation if there is no option.
    * [] likewise liquidity where pool exists but flipside hasn't indexed it yet.

# Storage
* At present Data is read from raw queries and proccessed each time the server starts up. 
    * Long downtimes cause this to sometimes be the expirience of page visitors.
    * We can separate events such that we only need to wait for preprocessing when loading new data, but not when updating files.

* [] Separate Model logic to have an interim post processed Clean Data that can greatly reduce loading speed.
    
<img src="static/images/data_flow.png"
     alt="Data Flow"
     style="float: left; margin: 10px; max-width: 100%;" />

    * [] Set up a default cutoff how many rounds back to go that can be overwritten.
        * Particularly for large Tables this should help cut down loading time.
        * Ability to overwrite ensures that data is still visible by the UI, but need to standardize. 

## Votium v2
* Votium recently updated to a V2 contract which conviently has the gauge address directly stored. 
* [] update votium to handle the new contract while supporting old contract data
    * [] once complete, add Votium to core gauge navigation widget  

## Establish first Experiments Component
* Locally select many filters to compare data. 
* [] launch experimental pages which allow these sorts of filtered comparisons to be viewed. 
    * Acceptable to be pretty specific
* [] harden standardized components for easier plug and play. 
''',
extensions=["fenced_code"]
)