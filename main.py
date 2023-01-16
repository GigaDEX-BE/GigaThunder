# get gui
import time

import pyqtgraph as pg
from gui.dashboard import get_dash
from gui.utils.FracLightGen import FracLightGen
from collections import deque

# TODO animate graph at 5 second intervals...

# TODO start workers
# TODO share pipes between gui and workers
# TODO draw actual me and obook lines...
# TODO print to console
# TODO make a trade
# TODO draw a line

dash, plot_item = get_dash()
dash.show()

# HIDE THIS AFTER THOUGH FFS, in like a class duh


counter = 0

t0_ms = (time.time()*1000)
xdata = deque([], maxlen=1_000)
ydata = deque([], maxlen=1_000)
benchmark = FracLightGen()
def update():
    global benchmark, plot_item, t0_ms, xdata, ydata
    price = benchmark.next()
    ts = int(time.time()*1000) - t0_ms
    xdata.append(ts)
    ydata.append(price)
    plot_item.setData(x=xdata, y=ydata)


timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)



pg.exec()

