import os
from workers.utils.dex_api_helper.dex_client import GigaDexClient
from dotenv import load_dotenv
import asyncio
import time
import traceback
from workers.utils.cancel_all import run_cancel_all
from workers.utils.me_price_feed import get_highest_bid_async, get_lowest_ask_async
from multiprocessing.connection import Connection
from workers.utils.get_full_state import get_orderbooks, get_compressed_orderbook
from workers.conf import consts as cn
import logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

FETCH_PERIOD_SEC = 5


class Fetcher:
    def __init__(self, guiConn, buttonsConn):
        self.guiConn: Connection = guiConn
        self.buttonsConn: Connection = buttonsConn
        pkstr = os.environ.get("pk_secret_hex")
        lot_account_pk_str = os.environ.get("lot_account_pk_str")
        self.uid = int(os.environ.get("bot_uid"))
        self.dexClient = GigaDexClient(lot_account_pk_str, pkstr)

        self.txd = []
        self.rxd = []

    async def run_loop(self):
        last_fetch_ts = 0
        last_bids = []
        last_asks = []
        while True:
            try:
                ts = time.time()
                if (ts - last_fetch_ts) > FETCH_PERIOD_SEC:
                    last_fetch_ts = ts
                    me_highest_bid, me_lowest_ask = await asyncio.gather(get_highest_bid_async(), get_lowest_ask_async())
                    me_bid = me_highest_bid / 1e9
                    me_ask = me_lowest_ask / 1e9
                    bids_nodes, asks_nodes = await get_orderbooks()
                    bids = get_compressed_orderbook(bids_nodes, is_ask=False)
                    asks = get_compressed_orderbook(asks_nodes, is_ask=True)
                    if len(bids) > 0:
                        last_bids = bids
                        gd_bid = bids[0][0]
                    else:
                        gd_bid = 0
                    if len(asks) > 0:
                        last_asks = asks
                        gd_ask = asks[0][0]
                    else:
                        gd_ask = 0
                    self.guiConn.send((me_bid, me_ask, gd_bid, gd_ask))
                else:
                    if self.buttonsConn.poll(0.001):
                        cmd = self.buttonsConn.recv()
                        if cmd == "CHECK":
                            logging.info(last_asks)
                            logging.info(last_bids)
                        elif cmd == "CANCEL":
                            logging.info(f"cancelling")
                            await run_cancel_all(self.dexClient, self.uid)
                        else:
                            logging.info(f"claiming")
                            tx = await self.dexClient.claim_balance()
                            logging.info(f"claimed wiht: {tx}")

                await asyncio.sleep(cn.MAIN_LOOP_SLEEP)
            except:
                logging.error(traceback.format_exc())
                await asyncio.sleep(cn.MAIN_BREAK_SLEEP)
                await self.run_loop()


def fetcher_process(guiConn, buttonsConn):
    loop = asyncio.new_event_loop()
    reporter = Fetcher(guiConn, buttonsConn)
    loop.run_until_complete(reporter.run_loop())
