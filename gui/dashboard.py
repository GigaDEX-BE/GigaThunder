import numpy as np
from gui.custom_plot_class import get_plot_widget
import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.Qt import QtWidgets
import os
from dotenv import load_dotenv
import asyncio
import logging
from workers.utils.dex_api_helper.dex_client import GigaDexClient
load_dotenv()
logging.basicConfig(level=logging.INFO)


loop = asyncio.get_event_loop()
pkstr = os.environ.get("pk_secret_hex")
lot_account_pk_str = os.environ.get("lot_account_pk_str")
uid = int(os.environ.get("bot_uid"))
dexClient = GigaDexClient(lot_account_pk_str, pkstr)


def claim_helper(*args):
    logging.info(f"creating claim task and forgetting")
    _task = loop.create_task(dexClient.claim_balance())


def get_dash(txWashPipe, txButtons):
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

    d5 = Dock("Dock5 - Image", size=(500,100))

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

    solLabel = QtWidgets.QLabel("8.3 SOL")
    lotLabel = QtWidgets.QLabel('6000 LOTS')
    claimableLabel = QtWidgets.QLabel('Claimable: 0.4 SOL, 10 LOTS')

    def balanceSetter(sol, lots, csol, clots):
        solLabel.setText(f"{sol} SOL")
        lotLabel.setText(f"{lots} LOTS")
        claimableLabel.setText(f"Claimable: {csol} SOL, {clots} LOTS")

    w1.addWidget(solLabel, row=0, col=0)
    w1.addWidget(lotLabel, row=0, col=1)
    w1.addWidget(claimableLabel, row=1, col=0)
    d1.addWidget(w1)

    w2 = ConsoleWidget()
    d2.addWidget(w2)

    w3, plot_item, ask_line, bid_line = get_plot_widget(txWashPipe)
    d3.addWidget(w3)

    w4 = pg.PlotWidget(title="Dock 4 plot")
    w4.plot(np.random.normal(size=100))
    d4.addWidget(w4)

    # TODO remove
    # w5 = pg.ImageView()
    # w5.setImage(np.random.normal(size=(100,100)))

    # TODO but a bunch of buttons in here instead
    buttonLayout = pg.LayoutWidget()
    b1 = QtWidgets.QPushButton('Check Open')
    b2 = QtWidgets.QPushButton('Cancel')
    b3 = QtWidgets.QPushButton('Benchmark')
    b4 = QtWidgets.QPushButton('Claim')

    b1.clicked.connect(lambda: txButtons.send("CHECK"))
    b2.clicked.connect(lambda: txButtons.send("CANCEL"))
    # b3.clicked.connect(lambda: txButtons.send("BENCHMARK"))
    b4.clicked.connect(lambda: txButtons.send("CLAIM"))


    buttonLayout.addWidget(b1, row=0, col=0)
    buttonLayout.addWidget(b2, row=0, col=1)
    buttonLayout.addWidget(b3, row=1, col=0)
    buttonLayout.addWidget(b4, row=1, col=1)
    d5.addWidget(buttonLayout)

    w6 = pg.PlotWidget(title="Dock 6 plot")
    w6.plot(np.random.normal(size=100))
    d6.addWidget(w6)
    return win, plot_item, ask_line, bid_line, balanceSetter



    # win.show()



# if __name__ == '__main__':
#     pg.exec()
