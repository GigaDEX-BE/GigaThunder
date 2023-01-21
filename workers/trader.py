import time
from workers.conf import consts as cn
import asyncio
from collections import deque
import os
import traceback
import logging
from asyncio.tasks import Task
from multiprocessing.connection import Connection
from workers.utils.dex_api_helper.dex_client import GigaDexClient
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)

TO_SEND_THRESHOLD = 10


class Trader:
    def __init__(self, rx_conn, sigs_conn):
        self.rx_conn: Connection = rx_conn
        self.sigs_conn: Connection = sigs_conn

        # init dex client
        pkstr = os.environ.get("pk_secret_hex")
        lot_account_pk_str = os.environ.get("lot_account_pk_str")
        custom_rpc_url = os.environ.get("custom_rpc_url")
        self.dexClient = GigaDexClient(lot_account_pk_str, pkstr, custom_rpc_url=custom_rpc_url)
        self.latencies = deque([], maxlen=100)
        self.sigs = deque([], maxlen=100)
        self.recent_prices = deque([], maxlen=100)
        self.to_send = []
        self.num_fails = 0
        self.num_trades = 0
        self.num_unconfirmed = 0
        self.num_dup_price_skips = 0

    def trade_callback(self, task: Task): # TODO so many repeats...??????
        task_name = str(task.get_name())
        t0, price = task_name.split(",")
        t0 = int(t0)
        price = int(price)
        dt = int(time.time()*1000) - t0
        try:
            sig = task.result()
            logging.info(f"{sig} @ {dt} @ {price}")
            self.latencies.append(dt)
            self.sigs.append(str(sig))
            self.num_trades += 1
            self.to_send.append((str(sig), dt, ))
        except Exception as e:
            logging.error(f"GOT CALLBACK ERR TYPE {e}")
            self.num_fails += 1
        finally:
            # TODO remove done callback
            # TODO, possible that its coz not most recent repeat...
            # task.remove_done_callback(self.trade_callback)
            pass

    async def send_results(self):
        try:
            self.sigs_conn.send(list(self.to_send))
            self.to_send = []
        except Exception as e:
            logging.error(f"ERROR IN SEND RESULTS FROM TRADER: {e}")

    async def run_loop(self):
        try:
            logging.info(f"{self.dexClient.keypair.pubkey()}")
            logging.info(await self.dexClient.get_wallet_balance())
            while True:
                if self.rx_conn.poll(cn.POLL_TIME_SEC):
                    floor_price_sol = self.rx_conn.recv()
                    floor_price_lams = int(floor_price_sol * 1e9)
                    lams_per_lot = int(floor_price_lams / 1e3)


                    # TODO
                    rand_lots = randint(int(-1*RAND_PRICE_RANGE), RAND_PRICE_RANGE)
                    rand_sol = rand_lots / 1e9

                    if lams_per_lot in self.recent_prices:
                        self.num_dup_price_skips += 1
                        continue
                    else:
                        self.recent_prices.append(lams_per_lot)
                    coro = self.dexClient.limit_sell_market_buy(lams_per_lot, 1)
                    task = asyncio.create_task(coro, name=f"{int(time.time()*1000)},{lams_per_lot}")
                    task.add_done_callback(self.trade_callback)
                if len(self.to_send) > TO_SEND_THRESHOLD:
                    await self.send_results()
                await asyncio.sleep(cn.MAIN_LOOP_SLEEP)
        except Exception as _e:
            logging.error(f"=====================RESETTING TRADER=================")
            logging.error(traceback.format_exception())
            await asyncio.sleep(cn.MAIN_BREAK_SLEEP)
            await self.run_loop()


def trader_process(rx_conn, sigs_conn):
    loop = asyncio.new_event_loop()
    trader = Trader(rx_conn, sigs_conn)
    loop.run_until_complete(trader.run_loop())









