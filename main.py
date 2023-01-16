# get gui
import logging
import time
from workers.fetcher import fetcher_process
from multiprocessing import Process, Pipe
import pyqtgraph as pg
from gui.dashboard import get_dash
from gui.utils.FracLightGen import FracLightGen
from collections import deque


# init pipes
rpxTrader, txpTrader = Pipe(duplex=False)
rpxGui, txpGui = Pipe(duplex=False)

# start workers
fetcherProcess = Process(target=fetcher_process, args=(txpTrader, txpGui, ))
fetcherProcess.start()



# TODO share pipes between gui and workers
# TODO draw actual me and obook lines...
# TODO print to console
# TODO make a trade
# TODO draw a line

dash, plot_item, ask_line, bid_line = get_dash()
dash.show()

# HIDE THIS AFTER THOUGH FFS, in like a class duh


NUM_TIME_SAMPLES = 800

xdata = deque([], maxlen=NUM_TIME_SAMPLES)
ydata = deque([], maxlen=NUM_TIME_SAMPLES)
benchmark = FracLightGen()


def update():
    global benchmark, plot_item, xdata, ydata, rpxGui, ask_line, bid_line
    price = benchmark.next()
    xdata.append(time.time())
    ydata.append(price)
    plot_item.setData(x=xdata, y=ydata)
    # TODO send to trader to execute when in benchmark mode

    if rpxGui.poll(0.001):
        me_bid, me_ask, gd_bid, gd_ask = rpxGui.recv()
        logging.info(f"gd: {gd_bid}, {gd_ask}")
        bid_line.setValue(me_bid)
        ask_line.setValue(me_ask)
        benchmark.floor = me_bid
        benchmark.ceiling = me_ask


timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(16)



pg.exec()

