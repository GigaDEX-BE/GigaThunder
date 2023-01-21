# get gui
import logging
import time
import traceback
import numpy as np
from workers.fetcher import fetcher_process
from workers.trader import trader_process
from workers.balancer import balancer_process
from multiprocessing import Process, Pipe
from gui.utils.FracLightGen import FracLightGen
from collections import deque


GUI_MODE = False
NUM_TIME_SAMPLES = 800
BENCHMARK_TIME_SEC = 10
LOG_PERIOD_SEC = 5
MAIN_LOOP_SLEEP_TIME_SEC = 0.010


class BenchmarkController:

    def __init__(self):

        # state
        self.BENCHMARK_MODE = False

        # init pipes
        rpxTrader, self.txpTrader = Pipe(duplex=False)
        self.rpxGui, txpGui = Pipe(duplex=False)
        self.rxBalance, txBalance = Pipe(duplex=False)
        self.rxButtons, txButtons = Pipe(duplex=False)
        self.rxSigs, txSigs = Pipe(duplex=False)

        # start workers
        self.fetcherProcess = Process(target=fetcher_process, args=(txpGui, rxButtons ))
        self.fetcherProcess.start()
        self.traderProcess = Process(target=trader_process, args=(rpxTrader, txSigs, ))
        self.traderProcess.start()
        self.balancerProcess = Process(target=balancer_process, args=(txBalance, ))
        self.balancerProcess.start()

        self.benchmark = FracLightGen()

        self.xdata = deque([], maxlen=NUM_TIME_SAMPLES)
        self.ydata = deque([], maxlen=NUM_TIME_SAMPLES)
        self.confirmData = deque([], maxlen=NUM_TIME_SAMPLES)
        self.latencyData = deque([], maxlen=NUM_TIME_SAMPLES)

        self.bench_start_time = 0
        self.last_price = 55
        self.num_confirmed_txs = 0
        self.last_log_ts = time.time()
        self.loop_idx = 0

    def run_main_loop(self):
        self.loop_idx += 1
        if self.BENCHMARK_MODE:
            price = self.benchmark.next()
            self.xdata.append(time.time())
            self.ydata.append(price)
            self.txpTrader.send(price)
            if (time.time() - self.bench_start_time) > BENCHMARK_TIME_SEC:
                self.BENCHMARK_MODE = False
                self.last_price = price
                self.rxButtons.send("CLAIM")

        if self.rpxGui.poll(0.001):
            me_bid, me_ask, gd_bid, gd_ask = self.rpxGui.recv()
            self.benchmark.floor = me_bid
            self.benchmark.ceiling = me_ask

        if self.rxBalance.poll(0.001):
            bals = self.rxBalance.recv()
            logging.info(f"got new bals: {bals}")

        if self.rxSigs.poll(0.001):
            sig, dt = self.rxSigs.recv()
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
            if len(self.latencyData) > 0:
                logging.info(f"MEAN TX LATENCY: {np.mean(self.latencyData)}")
                logging.info(f"MED TX LATENCY: {np.median(self.latencyData)}")
                logging.info(f"MIN TX LATENCY: {np.min(self.latencyData)}")
                logging.info(f"MAX TX LATENCY: {np.max(self.latencyData)}")
            logging.info(f"====================================================\n")

    def run(self):
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





