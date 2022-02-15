from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from imap.Parser.Estimates import Estimates
from imap.Gui.MultiTimeSeriesPlotWidget import MultiTimeSeriesPlotWidget
from imap.Gui.CollapsiblePanel import CollapsiblePanel


class EstimatesWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._multiPlotWidgets = []

        self._panels = [
            CollapsiblePanel("Red Player"),
            CollapsiblePanel("Green Player"),
            CollapsiblePanel("Blue Player"),
            CollapsiblePanel("Team")
        ]

        layout = QVBoxLayout(self)
        for panel in self._panels:
            layout.addWidget(panel)
        layout.addStretch()

    def updateFor(self, timeStep: int):
        for plotWidget in self._multiPlotWidgets:
            plotWidget.updateFor(timeStep)

    def loadEstimates(self, estimates: Estimates):
        self._multiPlotWidgets.clear()

        # Player plots
        for i, playerSeries in enumerate(estimates.playerSeries):
            multiPlotWidget = MultiTimeSeriesPlotWidget(playerSeries)
            self._multiPlotWidgets.append(multiPlotWidget)
            self._panels[i].setCentralWidget(multiPlotWidget)

        # Team plots
        multiPlotWidget = MultiTimeSeriesPlotWidget(estimates.teamSeries)
        self._multiPlotWidgets.append(multiPlotWidget)
        self._panels[-1].setCentralWidget(multiPlotWidget)
