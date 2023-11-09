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

## Storage
* At present Data is read from raw queries and proccessed each time the server starts up. 
    * Long downtimes cause this to sometimes be the expirience of page visitors.
    * We can separate events such that we only need to wait for preprocessing when loading new data, but not when updating files.

* Separate Model logic to have an interim post processed Clean Data that can greatly reduce loading speed.
    * [X] Curve Tables (vast majority of processing time)
    * [] Snapshot Tables
    * [] Votium Tables
    
<img src="static/images/data_flow.png"
     alt="Data Flow"
     style="float: left; margin: 10px; max-width: 100%;" />

    * [] Set up a default cutoff how many rounds back to go that can be overwritten.
        * Particularly for large Tables this should help cut down loading time.
        * Ability to overwrite ensures that data is still visible by the UI, but need to standardize. 

## Curve Gauge Rounds
    * Currently only shows last closed round and compares to prior closed round. 
    * [] Create current round page
    * [] Create vote volume graph of vote change velocity each round
    * Current no handling of 50% type gauges.
        * [] Determine best way to present this info and its impact on the inflation recieved by other gauges. 
  

## Establish first Experiments Component
* Locally select many filters to compare data. 
* [] launch experimental pages which allow these sorts of filtered comparisons to be viewed. 
    * Acceptable to be pretty specific
    * [x] Compare Top Vote Changes
        * [] Update Navigation
    * [x] Targetted Vote / Liquidity Comparissons
        * [] Add to Navigation
* [] harden standardized components for easier plug and play. 

## Gauge Votes
* Edit table to display as tabs (currently all votes are not displayed): 
    * [X] Active Votes to tab format
    * [X] Inactive Votes to tab format
    * [X] All Votes include
* [x] Add charts for All Votes not just active


## Add Description of metholodgy to each page
    * [] Pages w/ direct queries
    * [] Pages assembled from other pages queries

## Processing liquidity
    * Takes like 10 minutes where significant time is taken to filter out shitcoins.
    * [] Revise process for less heavy burden on filtering.
    * [] Need to solve hacked assets which have no balance changes but price prior to hack since no trades/moves after drained.

## Investigate Oddities:
0x50161102a240b1456d770dbb55c76d8dc2d160aa: 'ETHwBETHCRV-gauge'
    Pool: 0xbfab6fa95e0091ed66058ad493189d2cb29385e6
        But can't link pool.
        

 0x2932a86df44fe8d2a706d8e9c5d51c24883423f5: 'FrxETH'
    Pool: 0xa1f8a6807c402e4a15ef4eba36528a3fed24e577
    But thinks pool is 
        0xbfab6fa95e0091ed66058ad493189d2cb29385e6: ETHwBETHCRV-gauge'

# Reorganize
* New Categorization
    * [] History
        * Current views of historic data
        * Apply pivot (view as current or by voter/round)
    * [| Current Events
        * Current weeks battle
    * [] Science
        * Current and new experiments

# New Views
* Convex
    * [] Locked
    * [] Delegate Snapshot
* StakeDAO
    * [] staked sdCRV
    * [] Locked (veSDT)
        * [] Delegated Locked (veSDT) 
    * [] Delegate Snapshot
* Votium v2
    * Votium recently updated to a V2 contract which conviently has the gauge address directly stored. 
    * [] update votium to handle the new contract while supporting old contract data
        * [] once complete, add Votium to core gauge navigation widget  

## Delegation Second Order Impact
    * [] Update known as to pull from delegations
        * [?] May require changes to displaying known as for delegates of multiple known addresses such as Votium.
    * [] Voter Page needs to be able to view as core voter and delegate applied to voting power
    
## Meta Governance Ranking
    * [] Merge governance power between entities to rank combined influence
''',
extensions=["fenced_code"]
)