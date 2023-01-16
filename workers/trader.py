import time
from workers.conf import consts as cn
import asyncio
import random
from collections import deque
import os
import traceback
import logging
from multiprocessing.connection import Connection
from workers.utils.dex_api_helper.dex_client import GigaDexClient
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)


class Trader:
    def __init__(self, rx_conn):
        self.rx_conn: Connection = rx_conn

        # init dex client
        pkstr = os.environ.get("pk_secret_hex")
        lot_account_pk_str = os.environ.get("lot_account_pk_str")
        self.dexClient = GigaDexClient(lot_account_pk_str, pkstr)
        self.latencies = deque([], maxlen=1000)
        self.num_fails = 0

    def trade_callback(self, task):
        dt = int(time.time()*1000) - int(task.get_name())
        try:
            sig = task.result()
            logging.info(sig)
            self.latencies.append(dt)
        except Exception as e:
            logging.error(traceback.format_exc())
            self.num_fails += 1

    async def run_loop(self):
        try:
            logging.info(f"{self.dexClient.keypair.pubkey()}")
            logging.info(await self.dexClient.get_wallet_balance())
            while True:
                if self.rx_conn.poll(cn.POLL_TIME_SEC):
                    price_sol = self.rx_conn.recv()
                    lams_per_lot = int(price_sol * 1e9 / 1e3)
                    coro = self.dexClient.limit_sell_market_buy(lams_per_lot, 1)
                    task = asyncio.create_task(coro, name=f"{int(time.time()*1000)}")
                    task.add_done_callback(self.trade_callback)
                await asyncio.sleep(cn.MAIN_LOOP_SLEEP)
        except Exception as _e:
            logging.error(traceback.format_exception())
            await asyncio.sleep(cn.MAIN_BREAK_SLEEP)
            await self.run_loop()


def trader_process(rx_conn):
    loop = asyncio.new_event_loop()
    trader = Trader(rx_conn)
    loop.run_until_complete(trader.run_loop())









