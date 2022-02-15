from typing import List
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from imap.Parser.Estimates import TimeSeries
from imap.Gui.TimeSeriesPlotWidget import TimeSeriesPlotWidget


class MultiTimeSeriesPlotWidget(QWidget):

    def __init__(self, timeSeries: List[TimeSeries]):
        super().__init__()

        self._plotWidgets = []
        layout = QVBoxLayout(self)
        for series in timeSeries:
            plotWidget = TimeSeriesPlotWidget(series)
            self._plotWidgets.append(plotWidget)
            layout.addWidget(plotWidget)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()

    def updateFor(self, timeStep: int):
        for plotWidget in self._plotWidgets:
            plotWidget.updateFor(timeStep)

    # def minimumSizeHint(self) -> QSize:
    #     return QSize(super().minimumSizeHint().width(), 150 * len(self._multiPlotWidgets))
    #
    # def sizeHint(self) -> QSize:
    #     return QSize(super().sizeHint().width(), 150 * len(self._multiPlotWidgets))
