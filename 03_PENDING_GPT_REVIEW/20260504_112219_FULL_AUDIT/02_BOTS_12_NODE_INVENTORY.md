# 12 机器人节点清单

生成时间: 2026-05-04 11:23:01
输出目录: /Users/luxiangnan/Desktop/Tianlu_V6_5_Workspace/00_INBOX/FULL_AUDIT_INPUT_20260504_112219

===== config files =====
-rw-r--r--  1 luxiangnan  staff  2118 Apr 23 07:19 /Users/luxiangnan/freqtrade/config_9090_overlay.json
-rw-r--r--  1 luxiangnan  staff  2145 Apr 23 07:19 /Users/luxiangnan/freqtrade/config_9091_overlay.json
-rw-r--r--  1 luxiangnan  staff  2229 Apr 23 07:19 /Users/luxiangnan/freqtrade/config_9092_overlay.json
-rw-r--r--  1 luxiangnan  staff  2750 Apr 30 12:37 /Users/luxiangnan/freqtrade/config_9093_overlay.json
-rw-r--r--  1 luxiangnan  staff  2774 Apr 27 22:37 /Users/luxiangnan/freqtrade/config_9094_overlay.json
-rw-r--r--  1 luxiangnan  staff  2774 Apr 27 22:37 /Users/luxiangnan/freqtrade/config_9095_overlay.json
-rw-r--r--  1 luxiangnan  wheel  2658 May  1 20:46 /Users/luxiangnan/freqtrade/config_9096_overlay.json
-rw-r--r--  1 luxiangnan  staff  2627 Apr 27 22:37 /Users/luxiangnan/freqtrade/config_9097_overlay.json
-rw-r--r--  1 luxiangnan  staff  1673 Apr 23 07:19 /Users/luxiangnan/freqtrade/config_9098_overlay.json
-rw-r--r--  1 luxiangnan  staff  1810 Apr 23 07:19 /Users/luxiangnan/freqtrade/config_9099_overlay.json
-rw-r--r--  1 luxiangnan  staff  1400 Apr 13 14:19 /Users/luxiangnan/freqtrade/config_shared.json

===== user_data dirs =====
/Users/luxiangnan/freqtrade/user_data
/Users/luxiangnan/freqtrade/user_data_gate15637798222
/Users/luxiangnan/freqtrade/user_data_gate17656685222
/Users/luxiangnan/freqtrade/user_data_gate85363904550
/Users/luxiangnan/freqtrade/user_data_okx
/Users/luxiangnan/freqtrade/user_data_okx15637798222
/Users/luxiangnan/freqtrade/user_data_okx_15637798222
/Users/luxiangnan/freqtrade/user_data_okx_9093
/Users/luxiangnan/freqtrade/user_data_okx_9094
/Users/luxiangnan/freqtrade/user_data_okx_9095
/Users/luxiangnan/freqtrade/user_data_okx_9096
/Users/luxiangnan/freqtrade/user_data_okx_9097
/Users/luxiangnan/freqtrade/user_data_okx_9099
/Users/luxiangnan/freqtrade/user_data_tradesv3_gate_9093

===== config summary redacted =====

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_shared.json
dry_run: False
trading_mode: futures
margin_mode: isolated
stake_currency: USDT
stake_amount: unlimited
max_open_trades: 14
timeframe: 15m
strategy: FOttStrategy
bot_name: 天䘵
initial_state: running
force_entry_enable: True
cancel_open_orders_on_exit: True
exchange.name: None
exchange.has_key: False
exchange.has_secret: False
exchange.has_password: False
pair_whitelist_count: 0
api_server.enabled: None
api_server.listen_ip_address: None
api_server.listen_port: None
api_server.has_password: False

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9090_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_gate17656685222
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_gate17656685222/tradesv3_gate.sqlite?timeout=120&check_same_thread=False&pool_size=20
exchange.name: gateio
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: False
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9090
api_server.has_password: True

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9091_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_gate85363904550
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_gate85363904550/tradesv3_gate.sqlite?timeout=120&check_same_thread=False&pool_size=20
exchange.name: gateio
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: True
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9091
api_server.has_password: True

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9092_overlay.json
timeframe: 15m
user_data_dir: user_data_gate15637798222
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_gate15637798222/tradesv3_gate.sqlite?timeout=120&check_same_thread=False&pool_size=20
exchange.name: gateio
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: True
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9092
api_server.has_password: True

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9093_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_okx_9093
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_okx_9093/tradesv3_okx.sqlite?timeout=120
exchange.name: okx
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: False
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9093
api_server.has_password: True

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9094_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_okx_9094
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_okx_9094/tradesv3_okx.sqlite?timeout=120
exchange.name: okx
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: False
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9094
api_server.has_password: True

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9095_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_okx_9095
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_okx_9095/tradesv3_okx.sqlite?timeout=120
exchange.name: okx
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: False
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9095
api_server.has_password: True

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9096_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_okx_9096
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_okx_9096/tradesv3_okx.sqlite?timeout=120
exchange.name: okx
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: False
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9096
api_server.has_password: True

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9097_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_okx_9097
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_okx_9097/tradesv3_okx.sqlite?timeout=120
exchange.name: okx
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: False
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9097
api_server.has_password: True

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9098_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_okx_9098
exchange.name: okx
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: False
pair_whitelist_count: 5
api_server.enabled: None
api_server.listen_ip_address: None
api_server.listen_port: None
api_server.has_password: False

================================================================================
FILE: /Users/luxiangnan/freqtrade/config_9099_overlay.json
user_data_dir: /Users/luxiangnan/freqtrade/user_data_gate17656685222
db_url: sqlite:////Users/luxiangnan/freqtrade/user_data_gate17656685222/tradesv3_gate.sqlite
exchange.name: gateio
exchange.has_key: True
exchange.has_secret: True
exchange.has_password: False
pair_whitelist_count: 5
api_server.enabled: True
api_server.listen_ip_address: 0.0.0.0
api_server.listen_port: 9199
api_server.has_password: True

===== sqlite db files =====
/Users/luxiangnan/freqtrade/alert_db.db
/Users/luxiangnan/freqtrade/tradesv3.dryrun.sqlite
/Users/luxiangnan/freqtrade/tradesv3.sqlite
/Users/luxiangnan/freqtrade/tradesv3_9090.sqlite
/Users/luxiangnan/freqtrade/tradesv3_9091.sqlite
/Users/luxiangnan/freqtrade/tradesv3_binance.sqlite
/Users/luxiangnan/freqtrade/tradesv3_gate.sqlite
/Users/luxiangnan/freqtrade/user_data_gate15637798222/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_gate15637798222/tradesv3_gate.sqlite
/Users/luxiangnan/freqtrade/user_data_gate17656685222/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_gate17656685222/tradesv3_binance.sqlite
/Users/luxiangnan/freqtrade/user_data_gate17656685222/tradesv3_gate.sqlite
/Users/luxiangnan/freqtrade/user_data_gate85363904550/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_gate85363904550/tradesv3_gate.sqlite
/Users/luxiangnan/freqtrade/user_data_okx/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_okx/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx15637798222/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_okx15637798222/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9093/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9093/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9094/db_backups/position_sync_20260501_210032/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9094/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9094/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9095/db_backups/position_sync_20260501_210032/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9095/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9095/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9096/db_backups/ghost_cleanup_20260430_024445/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9096/db_backups/position_sync_20260501_210032/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9096/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9096/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9097/db_backups/position_sync_20260501_210032/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9097/tradesv3.sqlite
/Users/luxiangnan/freqtrade/user_data_okx_9097/tradesv3_okx.sqlite
/Users/luxiangnan/freqtrade/user_data_tradesv3_gate_9093/tradesv3_gate.sqlite
