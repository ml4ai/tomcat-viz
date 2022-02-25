from typing import Callable

from PyQt5.Qt import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from imap.Gui.CollapsiblePanel import CollapsiblePanel
from imap.Gui.MultiTimeSeriesPlotWidget import MultiTimeSeriesPlotWidget
from imap.Gui.Utils import createHorizontalSeparator, createVerticalSeparator
from imap.Parser.Estimates import Estimates


class EstimatesWidget(QWidget):

    def __init__(self, verticalStacking: bool = True, num_visible_time_steps: int = 5):
        super().__init__()

        self._num_visible_time_steps = num_visible_time_steps

        palette = QPalette()
        palette.setColor(QPalette.Active, QPalette.Window, QColor("white"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self._multiPlotWidgets = []
        self._legendToggleCallback = None
        self._searchChangeCallback = None

        self._panels = [
            CollapsiblePanel("Red Player", 0),
            CollapsiblePanel("Green Player", 1),
            CollapsiblePanel("Blue Player", 2),
            CollapsiblePanel("Team", 3)
        ]

        if verticalStacking:
            layout = QVBoxLayout(self)

            for panel in self._panels:
                layout.addWidget(panel)
                layout.addWidget(createHorizontalSeparator())
        else:
            layout = QHBoxLayout(self)

            for panel in self._panels:
                widgetLayout = QVBoxLayout()
                widgetLayout.setContentsMargins(0, 0, 0, 0)
                widgetLayout.addWidget(panel)
                layout.addLayout(widgetLayout)
                layout.addWidget(createVerticalSeparator())
                widgetLayout.addStretch()
        layout.addStretch()

    def updateFor(self, timeStep: int):
        for plotWidget in self._multiPlotWidgets:
            plotWidget.updateFor(timeStep)

    def loadEstimates(self, estimates: Estimates):
        self._multiPlotWidgets.clear()

        # Player plots
        for i, playerSeries in enumerate(estimates.playerSeries):
            multiPlotWidget = MultiTimeSeriesPlotWidget(playerSeries, i, self._num_visible_time_steps)
            multiPlotWidget.setLegendToggleCallback(self._legendToggleCallback)
            multiPlotWidget.setSearchChangeCallback(self._searchChangeCallback)
            self._multiPlotWidgets.append(multiPlotWidget)
            self._panels[i].setCentralWidget(multiPlotWidget)

        # Team plots
        multiPlotWidget = MultiTimeSeriesPlotWidget(estimates.teamSeries, len(estimates.playerSeries),
                                                    self._num_visible_time_steps)
        multiPlotWidget.setLegendToggleCallback(self._legendToggleCallback)
        multiPlotWidget.setSearchChangeCallback(self._searchChangeCallback)
        self._multiPlotWidgets.append(multiPlotWidget)
        self._panels[-1].setCentralWidget(multiPlotWidget)

    def setLegendToggleCallback(self, callback: Callable):
        self._legendToggleCallback = callback

    def toggleLegend(self, legendIndex: int, timeSeriesIndex: int, groupIndex: int):
        self._multiPlotWidgets[groupIndex].toggleLegend(legendIndex, timeSeriesIndex)

    def setPanelToggleCallback(self, callback: Callable):
        for panel in self._panels:
            panel.setToggleCallback(callback)

    def togglePanel(self, panelIndex: int):
        self._panels[panelIndex].toggle()

    def setSearchChangeCallback(self, callback: Callable):
        self._searchChangeCallback = callback

    def filterPlots(self, groupIndex: int, searchQuery: str):
        self._multiPlotWidgets[groupIndex].filterPlots(searchQuery)
