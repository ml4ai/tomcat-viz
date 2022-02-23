from typing import Callable, List
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from imap.Parser.Estimates import TimeSeries
from imap.Gui.TimeSeriesPlotWidget import TimeSeriesPlotWidget
from imap.Gui.Utils import createHorizontalSeparator


class MultiTimeSeriesPlotWidget(QWidget):

    def __init__(self, timeSeries: List[TimeSeries], groupIndex: int):
        super().__init__()

        self._plotWidgets = []
        self._onLegendToggleCallback = None
        self._groupIndex = groupIndex

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for i, series in enumerate(timeSeries):
            plotWidget = TimeSeriesPlotWidget(series, i)
            plotWidget.setLegendToggleCallback(self._onLegendToggle)
            self._plotWidgets.append(plotWidget)
            layout.addWidget(plotWidget)
            if i < len(timeSeries) - 1:
                layout.addWidget(createHorizontalSeparator())
        layout.addStretch()

    def updateFor(self, timeStep: int):
        for plotWidget in self._plotWidgets:
            plotWidget.updateFor(timeStep)

    def setLegendToggleCallback(self, callback: Callable):
        self._onLegendToggleCallback = callback

    def toggleLegend(self, legendIndex: int, timeSeriesIndex: int):
        self._plotWidgets[timeSeriesIndex].toggleLegend(legendIndex)

    def _onLegendToggle(self, legendIndex: int, timeSeriesIndex: int):
        if self._onLegendToggleCallback is not None:
            self._onLegendToggleCallback(legendIndex, timeSeriesIndex, self._groupIndex)
