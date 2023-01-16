import numpy as np
from gui.custom_plot_class import get_plot_widget
import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.Qt import QtWidgets

def get_dash():
    app = pg.mkQApp("DockArea Example")
    win = QtWidgets.QMainWindow()
    area = DockArea()
    win.setCentralWidget(area)
    win.resize(1000,500)
    win.setWindowTitle('pyqtgraph example: dockarea')

    d1 = Dock("Dock1", size=(1, 1))     ## give this dock the minimum possible size
    d2 = Dock("Dock2 - Console", size=(500,300), closable=True)
    d3 = Dock("Dock3", size=(500,400))
    d4 = Dock("Dock4 (tabbed) - Plot", size=(500,200))

    d5 = Dock("Dock5 - Image", size=(500,200))

    d6 = Dock("Dock6 (tabbed) - Plot", size=(500,200))
    area.addDock(d1, 'left')
    area.addDock(d2, 'right')
    area.addDock(d3, 'bottom', d1)
    area.addDock(d4, 'right')
    area.addDock(d5, 'left', d1)
    area.addDock(d6, 'top', d4)

    area.moveDock(d4, 'top', d2)
    area.moveDock(d6, 'above', d4)
    area.moveDock(d5, 'top', d2)

    ## first dock gets save/restore buttons
    w1 = pg.LayoutWidget()
    label = QtWidgets.QLabel("PoopyFart")
    saveBtn = QtWidgets.QPushButton('Save dock state')
    restoreBtn = QtWidgets.QPushButton('Restore dock state')
    restoreBtn.setEnabled(False)
    w1.addWidget(label, row=0, col=0)
    w1.addWidget(saveBtn, row=1, col=0)
    w1.addWidget(restoreBtn, row=2, col=0)
    d1.addWidget(w1)
    state = None
    def save():
        global state
        state = area.saveState()
        restoreBtn.setEnabled(True)
    def load():
        global state
        area.restoreState(state)
    saveBtn.clicked.connect(save)
    restoreBtn.clicked.connect(load)

    w2 = ConsoleWidget()
    d2.addWidget(w2)

    w3, plot_item, ask_line, bid_line = get_plot_widget()
    d3.addWidget(w3)

    w4 = pg.PlotWidget(title="Dock 4 plot")
    w4.plot(np.random.normal(size=100))
    d4.addWidget(w4)

    # TODO remove
    w5 = pg.ImageView()
    w5.setImage(np.random.normal(size=(100,100)))

    # TODO but a bunch of buttons in here instead
    buttonLayout = pg.LayoutWidget()
    b1 = QtWidgets.QPushButton('BUY')
    b2 = QtWidgets.QPushButton('SELL')
    b3 = QtWidgets.QPushButton('BENCHMARK')
    b4 = QtWidgets.QPushButton('CLAIM')

    buttonLayout.addWidget(b1, row=0, col=0)
    buttonLayout.addWidget(b2, row=0, col=1)
    buttonLayout.addWidget(b3, row=1, col=0)
    buttonLayout.addWidget(b4, row=1, col=1)
    d5.addWidget(buttonLayout)

    w6 = pg.PlotWidget(title="Dock 6 plot")
    w6.plot(np.random.normal(size=100))
    d6.addWidget(w6)
    return win, plot_item, ask_line, bid_line



    # win.show()



# if __name__ == '__main__':
#     pg.exec()
