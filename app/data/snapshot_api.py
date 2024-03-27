# -*- coding: utf-8 -*-
import requests
from pprint import pprint
import textwrap
import pdb

def run_query(q):
    # endpoint where you are making the request
    request = requests.post('https://hub.snapshot.org/graphql'
                            '',
                            json={'query': q})
    if request.status_code == 200:
        return request.json()
    else:
        # pdb.set_trace()
        raise Exception('Query failed. return code is {}.      {}'.format(request.status_code, q))


def get_space(space_address):
    query = f"""{{
    space(id: "{space_address}") {{
        id
        name
        about
        network
        symbol
        members
      }}
  }}
    """
    results = run_query(query)
    if results:
        return results['data']['space']
    return results

# {
#   "data": {
#     "space": {
#       "id": "yam.eth",
#       "name": "Yam Finance",
#       "about": "",
#       "network": "1",
#       "symbol": "YAM",
#       "members": [
#         "0x683A78bA1f6b25E29fbBC9Cd1BFA29A51520De84",
#         "0x9Ebc8AD4011C7f559743Eb25705CCF5A9B58D0bc",
#         "0xC3edCBe0F93a6258c3933e86fFaA3bcF12F8D695",
#         "0xbdac5657eDd13F47C3DD924eAa36Cf1Ec49672cc",
#         "0xEC3281124d4c2FCA8A88e3076C1E7749CfEcb7F2"
#       ]
#     }
#   }
# }

def get_spaces(first, skip):
    query = f'''{{
      spaces(
        first: {first},
        skip: {skip},
        orderBy: "created",
        orderDirection: asc
      ) {{
        id
        name
        about
        network
        symbol
        strategies {{
          name
          params
        }}
        admins
        members
        filters {{
          minScore
          onlyMembers
        }}
        plugins
      }}
  }}
    '''
    results = run_query(query)
    if results:
        return results['data']['spaces']
    return results

#     {
#   "data": {
#     "spaces": [
#       {
#         "id": "bonustrack.eth",
#         "name": "Fabien",
#         "about": "",
#         "network": "1",
#         "symbol": "TICKET",
#         "strategies": [
#           {
#             "name": "erc20-balance-of",
#             "params": {
#               "symbol": "DAI",
#               "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
#               "decimals": 18
#             }
#           }
#         ],
#         "admins": [],
#         "members": [
#           "0x24A12Fa313F57aF541d447c594072A992c605DCf"
#         ],
#         "filters": {
#           "minScore": 0,
#           "onlyMembers": false
#         },
#         "plugins": {
#           "quorum": {
#             "total": 500,
#             "strategy": "static"
#           }
#         }
#       }
#     ]
#   }
# }

def get_proposal(proposal_id):
    query = f"""
    {{
      proposal(id:"{proposal_id}") {{
        id
        title
        body
        choices
        start
        end
        snapshot
        state
        author
        created
        plugins
        network
        strategies {{
          name
          params
        }}
        space {{
          id
          name
        }}
      }}
    }}
    """
    results = run_query(query)
    if results:
        return results['data']['proposal']
    return results
# {
#   "data": {
#     "proposal": {
#       "id": "QmWbpCtwdLzxuLKnMW4Vv4MPFd2pdPX71YBKPasfZxqLUS",
#       "title": "Select Initial Umbrella Metapool",
#       "body": "Eventually, we hope that anyone will be able to create a metapool and fund a protection market for their project, but right now we want to start small and pick one pool that we will debut as a beta launch for Umbrella that will help us gather information and insight into the state of the market. In the future we can have all of these and more. Here are the choices:\n### Option 1: BlueChips MetaPool\n\nYou might consider this the safest of the pools. It contains a collection of different “blue-chip projects” across multiple verticals that have proven track records and are considered industry leaders. These include:\n\n* (3) Bluechip protocols: MakerDAO, Compound, and Uniswap. These are commonly seen as the most battletested and trusted DeFi projects on Ethereum.\n* (2) Centralized exchanges: Coinbase and Binance. These are the most popular and generally considered to be most reputable exchanges around. *note: Payout occurs only if Safu funds or the exchange’s insurance do not cover losses.\n* (2) Hardware Wallet companies, Ledger and Trezor, including the Ledger Nano S and X, and the Trezor Model T and One. This would cover large scale exploits in their hardware or firmware and would not cover individual loss due to phishing or poor security.\n\n### Option 2: Hot New Projects MetaPool\n\nThis pool targets newer projects on Ethereum that are considered reputable and have high TVL but are less battle tested and therefore may be more risky. While they may be more risky, this may mean that there is more demand for coverage for them in the market. This list is preliminary but internal discussions considered including:\n\n * Alchemix\n*  OHM\n*  Liquity\n*  FEI\n*  Integral\n*  Reflexer\n\n### Option 3: Integrated DegenV2 MetaPool\n\nThis last option focuses more closely on YAM products, specifically DegenV2 and the constituent protocols that it uses. This option would let us insure our own users and potentially test out our products in a more limited environment. The covered protocols would be:\n\n * UMA\n * Sushiswap/Uniswap depending on where our pools live\n * Any YAM contracts that are used\n *  Any future contracts included in future versions of Degen.\n\n### Choose wisely!\n",
#       "choices": [
#         "Option 1: BlueChips MetaPool",
#         "Option 2: Hot New Projects MetaP",
#         "Option 3: Integrated DegenV2 Met"
#       ],
#       "start": 1620676800,
#       "end": 1620806400,
#       "snapshot": "12408670",
#       "state": "closed",
#       "author": "0xEC3281124d4c2FCA8A88e3076C1E7749CfEcb7F2",
#       "space": {
#         "id": "yam.eth",
#         "name": "Yam Finance"
#       }
#     }
#   }
# }


def get_proposals(space_id, first, skip):
    query = f"""
    {{
      proposals (
        first: {first},
        skip: {skip},
        where: {{
          space_in: ["{space_id}"],
        }},
        orderBy: "created",
        orderDirection: desc
      ) {{
        id
        title
        body
        choices
        start
        end
        snapshot
        state
        author
        scores
        scores_by_strategy
        scores_total
        scores_updated

        space {{
          id
          name
        }}
      }}
    }}
    """
    results = run_query(query)
    if results:
        # print(results['data']['proposals'])
        return results['data']['proposals']
    return results
# {
#   "data": {
#     "proposals": [
#       {
#         "id": "QmWbpCtwdLzxuLKnMW4Vv4MPFd2pdPX71YBKPasfZxqLUS",
#         "title": "Select Initial Umbrella Metapool",
#         "body": "Eventually, we hope that anyone will be able to create a metapool and fund a protection market for their project, but right now we want to start small and pick one pool that we will debut as a beta launch for Umbrella that will help us gather information and insight into the state of the market. In the future we can have all of these and more. Here are the choices:\n### Option 1: BlueChips MetaPool\n\nYou might consider this the safest of the pools. It contains a collection of different “blue-chip projects” across multiple verticals that have proven track records and are considered industry leaders. These include:\n\n* (3) Bluechip protocols: MakerDAO, Compound, and Uniswap. These are commonly seen as the most battletested and trusted DeFi projects on Ethereum.\n* (2) Centralized exchanges: Coinbase and Binance. These are the most popular and generally considered to be most reputable exchanges around. *note: Payout occurs only if Safu funds or the exchange’s insurance do not cover losses.\n* (2) Hardware Wallet companies, Ledger and Trezor, including the Ledger Nano S and X, and the Trezor Model T and One. This would cover large scale exploits in their hardware or firmware and would not cover individual loss due to phishing or poor security.\n\n### Option 2: Hot New Projects MetaPool\n\nThis pool targets newer projects on Ethereum that are considered reputable and have high TVL but are less battle tested and therefore may be more risky. While they may be more risky, this may mean that there is more demand for coverage for them in the market. This list is preliminary but internal discussions considered including:\n\n * Alchemix\n*  OHM\n*  Liquity\n*  FEI\n*  Integral\n*  Reflexer\n\n### Option 3: Integrated DegenV2 MetaPool\n\nThis last option focuses more closely on YAM products, specifically DegenV2 and the constituent protocols that it uses. This option would let us insure our own users and potentially test out our products in a more limited environment. The covered protocols would be:\n\n * UMA\n * Sushiswap/Uniswap depending on where our pools live\n * Any YAM contracts that are used\n *  Any future contracts included in future versions of Degen.\n\n### Choose wisely!\n",
#         "choices": [
#           "Option 1: BlueChips MetaPool",
#           "Option 2: Hot New Projects MetaP",
#           "Option 3: Integrated DegenV2 Met"
#         ],
#         "start": 1620676800,
#         "end": 1620806400,
#         "snapshot": "12408670",
#         "state": "closed",
#         "author": "0xEC3281124d4c2FCA8A88e3076C1E7749CfEcb7F2",
#         "space": {
#           "id": "yam.eth",
#           "name": "Yam Finance"
#         }
#       },
#       ...
#     ]
#   }
# }


def get_vote(vote_id):
    query = """
    query {
      vote (
        id: "{}"
      ) {
        id
        voter
        created
        proposal
        choice
        space {
          id
        }
      }
    }
    """.format(vote_id)
    results = run_query(query)
    if results:
        return results['data']['vote']
    return results

# {
#   "data": {
#     "vote": {
#       "id": "QmeU7ct9Y4KLrh6F6mbT1eJNMkeQKMSnSujEfMCfbRLCMp",
#       "voter": "0x96176C25803Ce4cF046aa74895646D8514Ea1611",
#       "created": 1621183227,
#       "proposal": "QmPvbwguLfcVryzBRrbY4Pb9bCtxURagdv1XjhtFLf3wHj",
#       "choice": 1,
#       "space": {
#         "id": "spookyswap.eth"
#       }
#     }
#   }
# }

def get_votes(proposal_id):
    query = f"""
    query {{
      votes (
        first: 1000,
        skip: 0,
        where: {{
          proposal: "{proposal_id}"
        }},
        orderBy: "created",
        orderDirection: desc
      ) {{
        id
        voter
        vp
        vp_by_strategy
        vp_state
        created
        proposal {{
          id
        }}
        choice
        space {{
          id
        }}
      }}
    }}
    """
    results = run_query(query)
    if results:
        return results['data']['votes']
    return results

# {
#   "data": {
#     "votes": [
#       {
#         "id": "QmeU7ct9Y4KLrh6F6mbT1eJNMkeQKMSnSujEfMCfbRLCMp",
#         "voter": "0x96176C25803Ce4cF046aa74895646D8514Ea1611",
#         "created": 1621183227,
#         "proposal": "QmPvbwguLfcVryzBRrbY4Pb9bCtxURagdv1XjhtFLf3wHj",
#         "choice": 1,
#         "space": {
#           "id": "spookyswap.eth"
#         }
#       },
#       {
#         "id": "QmZ2CV86QH6Q6z7L6g7yJWS3HfgD9aQ3uTYYMXkMa5trHf",
#         "voter": "0x2686EaD94C5042e56a41eDde6533711a4303CC52",
#         "created": 1621181827,
#         "proposal": "QmPvbwguLfcVryzBRrbY4Pb9bCtxURagdv1XjhtFLf3wHj",
#         "choice": 1,
#         "space": {
#           "id": "spookyswap.eth"
#         }
#       },
#       ...
#     ]
#   }
# }


def get_vote_power(space_id, proposal_id, voter_address):
    query = f"""
    query {{
    vp (
        voter: "{voter_address}"
        space: "{space_id}"
        proposal: "{proposal_id}"
    ) {{
        vp
        vp_by_strategy
        vp_state
    }} 
    }}
    """
    results = run_query(query)
    if results:
        return results['data']['votes']
    return results

