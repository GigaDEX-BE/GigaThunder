import time
import os
from workers.utils.dex_api_helper.dex_client import GigaDexClient
from workers.utils.get_full_state import get_balances
from dotenv import load_dotenv
from workers.conf import consts as cn
import asyncio
import logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

# init
pkstr = os.environ.get("pk_secret_hex")
lot_account_pk_str = os.environ.get("lot_account_pk_str")
uid = int(os.environ.get("bot_uid"))
dexClient = GigaDexClient(lot_account_pk_str, pkstr)
loop = asyncio.get_event_loop()
print(f"bot pubkey: {dexClient.keypair.pubkey()}")

# get balances
balances_local = loop.run_until_complete(dexClient.get_wallet_balance())
balances_dex = loop.run_until_complete(get_balances())[uid]

local_lams = balances_local['lamports']
local_lots = balances_local['total_lots']
dex_lams = balances_dex[0]
dex_lots = balances_dex[1]

print(f"local SOL: {local_lams/1e9}")
print(f"local LOTS: {local_lots}")
print(f"DEX SOL: {dex_lams/1e9}")
print(f"DEX LOTS: {dex_lots}")

# claim
tx = loop.run_until_complete(dexClient.claim_balance())
print(f"claim_tx: {tx}")








