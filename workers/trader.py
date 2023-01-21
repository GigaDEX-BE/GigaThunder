import time
from workers.conf import consts as cn
import asyncio
import numpy as np
import random
from solana.rpc.core import UnconfirmedTxError
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
    def __init__(self, rx_conn, sigs_conn):
        self.rx_conn: Connection = rx_conn
        self.sigs_conn: Connection = sigs_conn

        # init dex client
        pkstr = os.environ.get("pk_secret_hex")
        lot_account_pk_str = os.environ.get("lot_account_pk_str")
        self.dexClient = GigaDexClient(lot_account_pk_str, pkstr)
        self.latencies = deque([], maxlen=100)
        self.num_fails = 0
        self.num_trades = 0
        self.num_unconfirmed = 0

    def trade_callback(self, task):
        dt = int(time.time()*1000) - int(task.get_name())
        try:
            sig = task.result()
            logging.info(sig)
            self.latencies.append(dt)
            self.num_trades += 1
            logging.info(f"mean confirmation: {np.mean(self.latencies)}, num trades: {self.num_trades}")
            self.sigs_conn.send((str(sig), dt))
        except UnconfirmedTxError:
            self.num_unconfirmed += 1
            logging.info(f"num_unconfirmed: {self.num_unconfirmed}")
        except Exception as e:
            logging.error(traceback.format_exc())
            self.num_fails += 1

    async def run_loop(self):
        try:
            logging.info(f"{self.dexClient.keypair.pubkey()}")
            logging.info(await self.dexClient.get_wallet_balance())
            last_price = None
            while True:
                if self.rx_conn.poll(cn.POLL_TIME_SEC):
                    price_sol = self.rx_conn.recv()
                    if price_sol == last_price:
                        continue
                    else:
                        last_price = price_sol
                    lams_per_lot = int(price_sol * 1e9 / 1e3)
                    coro = self.dexClient.limit_sell_market_buy(lams_per_lot, 1)
                    task = asyncio.create_task(coro, name=f"{int(time.time()*1000)}")
                    task.add_done_callback(self.trade_callback)
                    await self.dexClient.randomize_rpc()
                await asyncio.sleep(cn.MAIN_LOOP_SLEEP)
        except Exception as _e:
            logging.error(traceback.format_exception())
            await asyncio.sleep(cn.MAIN_BREAK_SLEEP)
            await self.run_loop()


def trader_process(rx_conn, sigs_conn):
    loop = asyncio.new_event_loop()
    trader = Trader(rx_conn, sigs_conn)
    loop.run_until_complete(trader.run_loop())









