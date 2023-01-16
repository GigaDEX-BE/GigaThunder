# get gui
import logging
import time
from workers.fetcher import fetcher_process
from workers.trader import trader_process
from workers.balancer import balancer_process
from multiprocessing import Process, Pipe
import pyqtgraph as pg
from gui.dashboard import get_dash
from gui.utils.FracLightGen import FracLightGen
from collections import deque


# init pipes
rpxTrader, txpTrader = Pipe(duplex=False)
rpxGui, txpGui = Pipe(duplex=False)
rxWashPipe, txWashPipe = Pipe(duplex=False)
rxBalance, txBalance = Pipe(duplex=False)
rxButtons, txButtons = Pipe(duplex=False)

# start workers
fetcherProcess = Process(target=fetcher_process, args=(txpGui, rxButtons ))
fetcherProcess.start()
traderProcess = Process(target=trader_process, args=(rpxTrader,))
traderProcess.start()
balancerProcess = Process(target=balancer_process, args=(txBalance, ))
balancerProcess.start()

# make the graph
dash, plot_item, ask_line, bid_line, balanceSetter, gd_bid_line, gd_ask_line = get_dash(txWashPipe, txButtons)
dash.show()

# HIDE THIS AFTER THOUGH FFS, in like a class duh

NUM_TIME_SAMPLES = 800

xdata = deque([], maxlen=NUM_TIME_SAMPLES)
ydata = deque([], maxlen=NUM_TIME_SAMPLES)
benchmark = FracLightGen()


BENCHMARK_MODE = False
BENCHMARK_TIME_SEC = 16
bench_start_time = 0

last_price = 62


def update():
    global benchmark, plot_item, xdata, ydata, rpxGui, ask_line, bid_line, txpTrader, BENCHMARK_MODE, last_price, bench_start_time, gd_ask_line, gd_bid_line
    if BENCHMARK_MODE:
        price = benchmark.next()
        xdata.append(time.time())
        ydata.append(price)
        plot_item.setData(x=xdata, y=ydata)
        txpTrader.send(price)
        if (time.time() - bench_start_time) > BENCHMARK_TIME_SEC:
            BENCHMARK_MODE = False
            last_price = price
    else:
        if rxWashPipe.poll(0.001):
            last_price = rxWashPipe.recv()
            if last_price == 88888888:
                BENCHMARK_MODE = True
                bench_start_time = time.time()
                return
            txpTrader.send(last_price)
        xdata.append(time.time())
        ydata.append(last_price)
        plot_item.setData(x=xdata, y=ydata)

    if rpxGui.poll(0.001):
        me_bid, me_ask, gd_bid, gd_ask = rpxGui.recv()
        # if gd_bid > 0:
        #     gd_bid_line.setValue(gd_bid)
        # if gd_ask > 0:
        #     gd_ask_line.setValue(gd_ask)
        bid_line.setValue(me_bid)
        ask_line.setValue(me_ask)
        benchmark.floor = me_bid
        benchmark.ceiling = me_ask

    if rxBalance.poll(0.001):
        bals = rxBalance.recv()
        balanceSetter(*bals)


timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)



pg.exec()

