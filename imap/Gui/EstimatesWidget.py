from typing import List, Tuple
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from imap.Common.Format import secondsToTime
from imap.Parser.Estimates import Estimates
from imap.Gui.TimeSeriesPlotWidget import TimeSeriesPlotWidget

import numpy as np


class EstimatesWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._plotWidgets = []

        # series = {"A": np.random.rand(900).tolist()}
        # self._graphWidget1 = TimeSeriesPlotWidget(series, "Random Belief 1")
        # series = {"A": np.random.rand(900).tolist()}
        # self._graphWidget2 = TimeSeriesPlotWidget(series, "Random Belief 2")
        # series = {"A": np.random.rand(900).tolist()}
        # self._graphWidget3 = TimeSeriesPlotWidget(series, "Random Belief 3")
        # series = {"A": np.random.rand(900).tolist()}
        # self._graphWidget4 = TimeSeriesPlotWidget(series, "Random Belief 4")
        # self._estimates = None

        self.setLayout(QVBoxLayout())

    def updateFor(self, timeStep: int):
        for plotWidget in self._plotWidgets:
            plotWidget.updateFor(timeStep)
        # self._graphWidget1.updateFor(timeStep)
        # self._graphWidget2.updateFor(timeStep)
        # self._graphWidget3.updateFor(timeStep)
        # self._graphWidget4.updateFor(timeStep)

    def loadEstimates(self, estimates: Estimates):
        # Remove currents widgets from the layout
        self._plotWidgets.clear()
        while self.layout().count():
            self.layout().takeAt(0).widget().deleteLater()

        # Add new plot widgets based on the time series in the estimates
        for playerSeries in estimates.playerSeries:
            for series in playerSeries:
                plotWidget = TimeSeriesPlotWidget(series)
                self._plotWidgets.append(plotWidget)
                self.layout().addWidget(plotWidget)

        for series in estimates.teamSeries:
            plotWidget = TimeSeriesPlotWidget(series)
            self._plotWidgets.append(plotWidget)
            self.layout().addWidget(plotWidget)
