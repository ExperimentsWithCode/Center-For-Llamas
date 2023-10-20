current_file_title = 'may_9'
fallback_file_title = 'may_1'


known_large_cvx_holders = {	
    'c2tp.eth': '0xaac0aa431c237c2c0b5f041c8e59b3f1a43ac78f',
	'frax': '0xb1748c79709f4ba2dd82834b8c82d4a505003f27',
	'Some Chad': '0x272b065A43EF59EA470fbfD9be76AD1b43aAB651',
	'BadgerDAO': '0xfd05d3c7fe2924020620a8be4961bbaa747e6305',
	'JPEGD': '0x51c2cef9efa48e08557a361b52db34061c025a1b',
	'Redacted': '0xa52fd396891e7a74b641a2cb1a6999fcf56b077e',
	'Mochi Inu': '0x597f540bb63381ffa267027d2d479984825057a8',
	'Reserve 1': '0xc6625129c9df3314a4dd604845488f4ba62f9db8',
	'Olympus': '0x2d643df5de4e9ba063760d475beaa62821c71681',
	'Keeper': '0x0d5dc686d0a2abbfdafdfb4d0533e886517d4e83',
	'Alchemix': '0x9e2b6378ee8ad2a4a95fe481d63caba8fb0ebbf9',
	'Origin': '0x70fce97d671e81080ca3ab4cc7a59aac2e117137',
	'Silo': '0xdff2aea378e41632e45306a6de26a7e0fd93ab07',
	'Tokemac': '0x8b4334d4812c530574bd4f2763fcd22de94a969b',
	'Paladin': '0xb95a4779ccedc53010ef0df8bf8ed6aeb0e8c2b2',
    'Pirex': '0x35A398425d9f1029021A92bc3d2557D42C8588D7',
    'Clever': '0x96c68d861ada016ed98c30c810879f9df7c64154',
    'Badger': '0x898111d1f4eb55025d0036568212425ee2274082',
    'Bent': '0xe001452bec9e7ac34ca4ecac56e7e95ed9c9aa3b',
    'Reserve': '0x578a4af5cbc3009487a89be88bc560157200795b',
    'StakeDAO': '0xf930ebbd05ef8b25b1797b9b2109ddc9b0d43063',
    'Origin': '0xc1aa82499da8d37383f1e6d95de417ecf7514e7c',
}



known_large_cvx_holders_addresses = {
    '0xaac0aa431c237c2c0b5f041c8e59b3f1a43ac78f' : 'c2tp.eth',
    '0xb1748c79709f4ba2dd82834b8c82d4a505003f27' : 'frax',
    '0x272b065A43EF59EA470fbfD9be76AD1b43aAB651' : 'some chad',
    '0xfd05d3c7fe2924020620a8be4961bbaa747e6305' : 'BadgerDAO',
    '0x51c2cef9efa48e08557a361b52db34061c025a1b' : 'JPEGD',
    '0xa52fd396891e7a74b641a2cb1a6999fcf56b077e' : 'Redacted',
    '0x597f540bb63381ffa267027d2d479984825057a8' : 'Mochi Inu',
    '0xc6625129c9df3314a4dd604845488f4ba62f9db8' : 'Reserve 1',
    '0x2d643df5de4e9ba063760d475beaa62821c71681' : 'Olympus',
    '0x0d5dc686d0a2abbfdafdfb4d0533e886517d4e83' : 'Keeper',
    '0x9e2b6378ee8ad2a4a95fe481d63caba8fb0ebbf9' : 'Alchemix',
    '0x70fce97d671e81080ca3ab4cc7a59aac2e117137' : 'Origin',
    '0xdff2aea378e41632e45306a6de26a7e0fd93ab07' : 'Silo', 
    '0x8b4334d4812c530574bd4f2763fcd22de94a969b' : 'Tokemac',
    '0xb95a4779ccedc53010ef0df8bf8ed6aeb0e8c2b2' : 'Paladin',
    '0x35A398425d9f1029021A92bc3d2557D42C8588D7' : 'Pirex',
    '0x96c68d861ada016ed98c30c810879f9df7c64154' : 'Clever',
    '0x898111d1f4eb55025d0036568212425ee2274082' : 'Badger',
    '0xe001452bec9e7ac34ca4ecac56e7e95ed9c9aa3b' : 'Bent',
    '0xde1e6a7ed0ad3f61d531a8a78e83ccddbd6e0c49' : 'Votium',
    # Non Votium Delegations
    '0x14f83ff95d4ec5e8812ddf42da1232b0ba1015e6' : 'Badger',	
    '0x58f1cac30786754d8128ca7a1e5cf8f29a780044' : 'Bent',	
    '0x5180db0237291a6449dda9ed33ad90a38787621c' : 'frax',	
    '0x9b8b04b6f82cd5e1dae58ca3614d445f93defc5c' : 'silo',	
    '0x131bd1a2827cceb2945b2e3b91ee1bf736ccbf80' : 'olympus',	
    '0x79e76c14b3bb6236dfc06d2d7ff219c8b070169c' : 'Reserve',	
    '0x68378fcb3a27d5613afcfddb590d35a6e751972c' : 'Paladin',	
    '0x8200d84590eceb10c6471268930e2924f34e3d69' : 'Bent',	
    '0xd733d4cc5b42206a62ed7b1ceec5b4d61898f429' : 'Reserve',
}




known_large_curve_holders = {
    '0x52f541764e6e90eebc5c21ff570de0e2d63766b6' : 'StakeDAO (sdCRV)',
    '0x49640905aae77308f1d35f370efd5c08a790f1cc' : '0xcalibur',
    '0xf147b8125d2ef93fb6965db97d6746952a133934' : 'Yearn (yCRV)',
    '0x0d5dc686d0a2abbfdafdfb4d0533e886517d4e83' : 'Keeper (KP3RETH)',
    '0xa52fd396891e7a74b641a2cb1a6999fcf56b077e' : 'Redacted?',
    '0xa0fb1b11cca5871fb0225b64308e249b97804e99' : 'Aladin',
    '0x989aeb4d175e16225e39e87d0d97a3360524ad80' : 'Convex (cvxCRV)',
    '0x847fa1a5337c7f24d7066e467f2e2a0f969ca79f' : 'Frax',
    '0xf06016d822943c42e3cb7fc3a6a3b1889c1045f8' : 'Liquity',
    '0x7a16ff8270133f063aab6c9977183d9e72835428' : 'CRV Founder',
    '0x52f737774c470e38b4f0109a2c852b129df14302': 'Wintermute(?)'
    }


gauge_names = {
    '0x875ce7e0565b4c8852ca2a9608f27b7213a90786': 'Curve Polygon Bridge Wrapper',
    '0xa90996896660decc6e997655e065b23788857849': 'Curve sUSDv2 Liquidity Gauge',
    '0x6aba93e10147f86744bb9a50238d25f49ed4f342': 'Curve.fi pitchFXS-f Gauge Deposit',
    '0xbfcf63294ad7105dea65aa58f8ae5be2d9d0952a': 'Curve.fi: DAI/USDC/USDT Gauge',
    '0x555766f3da968ecbefa690ffd49a2ac02f47aa5f': 'Curve Arbitrum Bridge Wrapper',
    '0xbb1b19495b8fe7c402427479b9ac14886cbbaaee': 'Polygon Mainnet',
    '0xce5f24b7a95e9cba7df4b54e911b4a3dc8cdaf6f': 'Arbitrum One',
    '0x172a5af37f69c69cc59e748d090a70615830a5dd': 'Optimism Mainnet',
    '0xc5ae4b5f86332e70f3205a8151ee9ed9f71e0797': 'Optimism Mainent (2)'
}

gauge_symbols = {
    '0x875ce7e0565b4c8852ca2a9608f27b7213a90786': 'PolygonBridge',
    '0xa90996896660decc6e997655e065b23788857849': 'sUSDv2-3CRV-gauge',
    '0x6aba93e10147f86744bb9a50238d25f49ed4f342': 'pitchFXS-f-gauge',
    '0xbfcf63294ad7105dea65aa58f8ae5be2d9d0952a': '3CRV-gauge',
    '0x555766f3da968ecbefa690ffd49a2ac02f47aa5f': 'ArbitrumBridge',
    '0xbb1b19495b8fe7c402427479b9ac14886cbbaaee': 'PolygonMainnet',
    '0xce5f24b7a95e9cba7df4b54e911b4a3dc8cdaf6f': 'ArbitrumOne',
    '0x172a5af37f69c69cc59e748d090a70615830a5dd': 'OptimismMainnet',
    '0xc5ae4b5f86332e70f3205a8151ee9ed9f71e0797': 'OptimismMainent(2)'

}

filename_curve_gauges = 'gauge_to_lp_map'

filename_curve_locker = 'curve_locker'
filename_curve_locker_supply = 'curve_locker_supply'
filename_curve_locker_withdraw = 'curve_locker_withdraw'
filename_curve_locker_deposit = 'curve_locker_deposit'
filename_curve_locker_history = 'curve_locker_history'
filename_curve_locker_current_locks = 'curve_locker_current_locks'
filename_curve_locker_known_locks = 'curve_locker_known_locks'

filename_curve_gauge_votes = 'curve_gauge_votes'
filename_curve_gauge_votes_all = 'curve_gauge_votes_all'
filename_curve_gauge_votes_formatted = 'curve_gauge_votes_formatted'
filename_curve_gauge_votes_current = 'curve_gauge_votes_current'

filename_curve_gauge_rounds_by_user = 'curve_gauge_rounds_by_user'
filename_curve_gauge_rounds_by_aggregate = 'curve_gauge_rounds_by_aggregate'

filename_curve_liquidity = 'curve_liquidity'
filename_curve_liquidity_aggregate = 'curve_liquidity_aggregate'