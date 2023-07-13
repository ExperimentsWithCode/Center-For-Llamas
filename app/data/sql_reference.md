# gauge_to_pool_map
SELECT 
  BLOCK_TIMESTAMP,
  DECODED_LOG:gauge::string as gauge_addr,
  DECODED_LOG:pool::string as pool_addr,
  contracts.NAME as gauge_name,
  contracts.SYMBOL as gauge_symbol,
  pool_contracts.NAME as pool_name,
  pool_contracts.SYMBOL as pool_symbol
FROM ethereum.core.ez_decoded_event_logs as logs
LEFT JOIN ethereum.core.dim_contracts as contracts
  ON logs.DECODED_LOG:gauge::string = contracts.ADDRESS
LEFT JOIN ethereum.core.dim_contracts as pool_contracts
  ON logs.DECODED_LOG:pool::string = pool_contracts.ADDRESS
WHERE logs.CONTRACT_ADDRESS = lower('0xB9fC157394Af804a3578134A6585C0dc9cc990d4')
AND logs.EVENT_NAME = 'LiquidityGaugeDeployed'

