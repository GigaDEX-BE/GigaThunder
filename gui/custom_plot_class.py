"""
This example demonstrates the creation of a plot with
DateAxisItem and a customized ViewBox.
"""

import numpy as np
from PySide6 import QtGui, QtCore
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        kwds['enableMenu'] = False
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)

    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.MouseButton.RightButton:
            self.autoRange()
        elif ev.button() == QtCore.Qt.MouseButton.LeftButton:
            # TODO print coordinates
            print(ev.pos())
            print(ev.scenePos())
            print(ev.screenPos())

    ## reimplement mouseDragEvent to disable continuous axis zoom
    def mouseDragEvent(self, ev, axis=None):
        if axis is not None and ev.button() == QtCore.Qt.MouseButton.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev, axis=axis)


class CustomTickSliderItem(pg.TickSliderItem):
    def __init__(self, *args, **kwds):
        pg.TickSliderItem.__init__(self, *args, **kwds)

        self.all_ticks = {}
        self._range = [0, 1]

    def setTicks(self, ticks):
        for tick, pos in self.listTicks():
            self.removeTick(tick)

        for pos in ticks:
            tickItem = self.addTick(pos, movable=False, color="#333333")
            self.all_ticks[pos] = tickItem

        self.updateRange(None, self._range)

    def updateRange(self, vb, viewRange):
        origin = self.tickSize / 2.
        length = self.length

        lengthIncludingPadding = length + self.tickSize + 2

        self._range = viewRange

        for pos in self.all_ticks:
            tickValueIncludingPadding = (pos - viewRange[0]) / (viewRange[1] - viewRange[0])
            tickValue = (tickValueIncludingPadding * lengthIncludingPadding - origin) / length

            # Convert from np.bool_ to bool for setVisible
            visible = bool(tickValue >= 0 and tickValue <= 1)

            tick = self.all_ticks[pos]
            tick.setVisible(visible)

            if visible:
                self.setTickValue(tick, tickValue)


# app = pg.mkQApp()

def get_plot_widget():
    axis = pg.DateAxisItem(orientation='bottom')
    vb = CustomViewBox()

    # TODO add line to custom viewbox

    pw = pg.PlotWidget(viewBox=vb, axisItems={'bottom': axis}, enableMenu=False,
                       title="PlotItem with DateAxisItem, custom ViewBox and markers on x axis<br>Menu disabled, mouse behavior changed: left-drag to zoom, right-click to reset zoom")

    me_ask_line = pg.InfiniteLine(pos=2, movable=True, pen=pg.mkPen("red"), angle=0)
    me_bid_line = pg.InfiniteLine(pos=7, movable=True, pen=pg.mkPen("red"), angle=0)
    pw.addItem(me_ask_line)
    pw.addItem(me_bid_line)


    dates = np.arange(8) * (3600 * 24 * 356)
    plot_item = pw.plot(x=dates, y=[1, 6, 2, 4, 3, 5, 6, 8])

    # Using allowAdd and allowRemove to limit user interaction
    tickViewer = CustomTickSliderItem(allowAdd=False, allowRemove=False)
    vb.sigXRangeChanged.connect(tickViewer.updateRange)
    pw.plotItem.layout.addItem(tickViewer, 4, 1)

    tickViewer.setTicks([dates[0], dates[2], dates[-1]])

    pw.setWindowTitle('pyqtgraph example: customPlot')

    return pw, plot_item, me_ask_line, me_bid_line


