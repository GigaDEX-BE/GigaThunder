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


CHECK_PERIOD_SEC = 1


class Balancer:
    def __init__(self, tx_conn):
        self.tx_conn = tx_conn
        pkstr = os.environ.get("pk_secret_hex")
        lot_account_pk_str = os.environ.get("lot_account_pk_str")
        self.uid = int(os.environ.get("bot_uid"))
        self.dexClient = GigaDexClient(lot_account_pk_str, pkstr)

    async def run_loop(self):
        try:
            last_fetch = time.time()
            sol = 0
            lots = 0
            csol = 0
            clots = 0
            while True:
                ts = time.time()
                if (ts - last_fetch) > CHECK_PERIOD_SEC:
                    last_fetch = ts
                    balances = await self.dexClient.get_wallet_balance()
                    _sol = balances['lamports'] / 1e9
                    _lots = balances['total_lots']
                    bals = await get_balances()
                    logging.info(bals)
                    _csol = bals[self.uid][0] / 1e9
                    _clots = bals[self.uid][1]

                    if sol != _sol or lots != _lots or csol != _csol or clots != _clots:
                        logging.info(f"got new bals")
                        sol = _sol
                        lots = _lots
                        csol = _csol
                        clots = _clots
                        self.tx_conn.send((sol, lots, csol, clots))

                await asyncio.sleep(cn.MAIN_LOOP_SLEEP)
        except:
            await asyncio.sleep(cn.MAIN_BREAK_SLEEP)
            await self.run_loop()


def balancer_process(tx_conn):
    loop = asyncio.new_event_loop()
    balancer = Balancer(tx_conn)
    loop.run_until_complete(balancer.run_loop())


