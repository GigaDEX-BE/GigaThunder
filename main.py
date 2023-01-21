# get gui
import logging
import time
import traceback
import numpy as np
from workers.fetcher import fetcher_process
from workers.trader import trader_process
from workers.balancer import balancer_process
from workers.subscriber import subscriber_process
from multiprocessing import Process, Pipe
from gui.utils.FracLightGen import FracLightGen
from collections import deque
from random import randint

GUI_MODE = False
RAND_PRICE_RANGE = int(5e2)
NUM_TIME_SAMPLES = 800
BENCHMARK_TIME_SEC = 4
LOG_PERIOD_SEC = 5
WORKER_START_DELAY = 3
MAIN_LOOP_SLEEP_TIME_SEC = 0.010
BENCHMARK_START_DELAY_SEC = 15


class BenchmarkController:

    def __init__(self):

        # state
        self.BENCHMARK_MODE = False

        # init pipes
        rpxTrader, self.txpTrader = Pipe(duplex=False)
        self.rpxGui, txpGui = Pipe(duplex=False)
        self.rxBalance, txBalance = Pipe(duplex=False)
        self.rxButtons, self.txButtons = Pipe(duplex=False)
        self.rxSigs, txSigs = Pipe(duplex=False)
        self.rxWsTrades, txWsTrades = Pipe(duplex=False)

        # start workers
        self.fetcherProcess = Process(target=fetcher_process, args=(txpGui, self.rxButtons ))
        self.fetcherProcess.start()
        self.traderProcess = Process(target=trader_process, args=(rpxTrader, txSigs, ))
        self.traderProcess.start()
        self.balancerProcess = Process(target=balancer_process, args=(txBalance, ))
        self.balancerProcess.start()
        self.subscriberProcess = Process(target=subscriber_process, args=(txWsTrades, ))
        self.subscriberProcess.start()

        self.workers = {
            'fetcher': self.fetcherProcess,
            'trader': self.traderProcess,
            'balancer': self.balancerProcess,
            'subscriber': self.subscriberProcess
        }

        self.benchmark = FracLightGen()

        self.confirmData = deque([], maxlen=NUM_TIME_SAMPLES)
        self.latencyData = deque([], maxlen=NUM_TIME_SAMPLES)

        self.bench_start_time = 0
        self.last_price = 55
        self.num_confirmed_txs = 0
        self.last_log_ts = time.time()
        self.loop_idx = 0
        self.last_loop_ts = time.time() # TODO measure loop latency
        self.ran_once = False
        self.init_ts = 0

    def run_main_loop(self):
        self.loop_idx += 1

        if not self.ran_once and (time.time() - self.init_ts) > BENCHMARK_START_DELAY_SEC:
            self.BENCHMARK_MODE = True
            self.ran_once = True
            self.bench_start_time = time.time()
            logging.info(f"Started Benchmark [ONCE]")

        if self.BENCHMARK_MODE:

            floor_price_sol = self.benchmark.next()

            # convert to lot in lams and randomize
            floor_price_lams = int(floor_price_sol * 1e9)
            lams_per_lot = int(floor_price_lams / 1e3)
            rand_lams = randint(int(-1*RAND_PRICE_RANGE), RAND_PRICE_RANGE)
            lams_per_lot += rand_lams

            # send to trader
            self.txpTrader.send(lams_per_lot)

            if (time.time() - self.bench_start_time) > BENCHMARK_TIME_SEC:
                self.BENCHMARK_MODE = False
                self.last_price = floor_price_sol
                self.txButtons.send("CLAIM")
                logging.info(f"FINISHED BENCHMARK")

        if self.rpxGui.poll(0.001):
            me_bid, me_ask, gd_bid, gd_ask = self.rpxGui.recv()
            self.benchmark.floor = me_bid
            self.benchmark.ceiling = me_ask

        if self.rxBalance.poll(0.001):
            bals = self.rxBalance.recv()
            logging.info(f"got new bals: {bals}")

        if self.rxSigs.poll(0.001):
            data = self.rxSigs.recv()
            for sig, dt, price in data:
                # TODO save price and match up...
                self.num_confirmed_txs += 1
                self.confirmData.append(self.num_confirmed_txs)
                self.latencyData.append(dt)

    def log_status(self):
        ts = time.time()
        if (ts - self.last_log_ts) > LOG_PERIOD_SEC:
            self.last_log_ts = ts
            logging.info(f"============loop_idx: {self.loop_idx}===============")
            logging.info(f"BENCHMARK_MODE: {self.BENCHMARK_MODE}")
            logging.info(f"NUM_CONFIRMED_txs: {self.num_confirmed_txs}")
            for k, v in self.workers.items():
                logging.info(f"{k} is alive: {v.is_alive()}")
            if len(self.latencyData) > 0:
                logging.info(f"MEAN TX LATENCY: {np.mean(self.latencyData)}")
                logging.info(f"MED TX LATENCY: {np.median(self.latencyData)}")
                logging.info(f"MIN TX LATENCY: {np.min(self.latencyData)}")
                logging.info(f"MAX TX LATENCY: {np.max(self.latencyData)}")
            logging.info(f"====================================================\n")

    def run(self):
        logging.info(f"Initial delay for workers to start: {WORKER_START_DELAY} Seconds")
        time.sleep(WORKER_START_DELAY)
        self.txButtons.send("CLAIM")
        self.init_ts = time.time()
        while True:
            try:
                self.run_main_loop()
                self.log_status()
                time.sleep(MAIN_LOOP_SLEEP_TIME_SEC)
            except Exception as e:
                logging.error(traceback.format_exc())


if __name__ == "__main__":
    benchmarkController = BenchmarkController()
    benchmarkController.run()





