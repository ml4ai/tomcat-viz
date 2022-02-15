from typing import List, Tuple
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtWidgets import QVBoxLayout

from imap.Common.Format import secondsToTime
from imap.Parser.Estimates import Estimates, TimeSeries
from imap.Gui.TimeSeriesPlotWidget import TimeSeriesPlotWidget
from imap.Gui.CollapsiblePanel import CollapsiblePanel

import numpy as np


class EstimatesWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._plotWidgets = []

        self._panels = [
            CollapsiblePanel("Red Player"),
            CollapsiblePanel("Green Player"),
            CollapsiblePanel("Blue Player"),
            CollapsiblePanel("Team")
        ]

        layout = QVBoxLayout()
        for panel in self._panels:
            layout.addWidget(panel)

        layout.addStretch()
        self.setLayout(layout)

        # for i in range(len(self._panels)):
        #     layout2 = QVBoxLayout()
        #     for _ in range(3):
        #         plotWidget = TimeSeriesPlotWidget(TimeSeries("Teste", [[0.1, 0.2, 0.3]]))
        #         self._plotWidgets.append(plotWidget)
        #         layout2.addWidget(plotWidget)
        #     self._panels[i].setContentLayout(layout2)

    def updateFor(self, timeStep: int):
        for plotWidget in self._plotWidgets:
            plotWidget.updateFor(timeStep)

    def loadEstimates(self, estimates: Estimates):
        # # Remove currents widgets from the layout
        # self._plotWidgets.clear()
        # # while self.layout().count():
        # #     self.layout().takeAt(0).widget().deleteLater()
        #
        # # Add new plot widgets based on the time series in the estimates
        # for i, playerSeries in enumerate(estimates.playerSeries):
        #     layout = QVBoxLayout()
        #     for series in playerSeries:
        #         plotWidget = TimeSeriesPlotWidget(series)
        #         self._plotWidgets.append(plotWidget)
        #         layout.addWidget(plotWidget)
        #     layout.addStretch()
        #     self._panels[i].setContentLayout(layout)
        #
        # for series in estimates.teamSeries:
        #     plotWidget = TimeSeriesPlotWidget(series)
        #     self._plotWidgets.append(plotWidget)
        #     layout = QVBoxLayout()
        #     layout.addWidget(plotWidget)
        #     layout.addStretch()
        #     self._panels[-1].setContentLayout(layout)

        for i in range(len(self._panels)):
            layout2 = QVBoxLayout()
            for _ in range(3):
                plotWidget = TimeSeriesPlotWidget(TimeSeries("Teste", [[0.1, 0.2, 0.3]]))
                self._plotWidgets.append(plotWidget)
                layout2.addWidget(plotWidget)
            self._panels[i].setContentLayout(layout2)

    def createWidget(self, color: str):
        widget = QWidget()
        widget.setStyleSheet(f"background-color:{color};")
        widget.setMinimumHeight(150)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        widget.show()

        return widget