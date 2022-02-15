from typing import Dict, List
from pyqtgraph import PlotWidget, mkPen
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QSizePolicy

from imap.Common.Format import secondsToTime
from imap.Parser.Estimates import TimeSeries


class TimeSeriesPlotWidget(PlotWidget):
    NUM_VISIBLE_TIME_STEPS = 20

    def __init__(self, series: TimeSeries):
        super().__init__()

        self._series = series
        self._times = list(range(series.size))
        self.setTitle(series.name)

        self._configure()
        self._initializePlot()

    def _configure(self):
        self.setBackground("white")
        self.setYRange(0, 1)
        self.setMouseEnabled(x=False, y=False)
        self.setMinimumHeight(150)
        self.setMaximumHeight(150)
        self.centralWidget.hideButtons()

        # self.palette = ...

    def _initializePlot(self):
        self._dataItems = []
        for _ in self._series.values:
            pen = mkPen(color=(0, 0, 255), width=2)  # get from palette later
            self._dataItems.append(self.plot([], [], pen=pen))
            break

        # Baseline
        pen = mkPen(color=(255, 0, 0), width=1, style=Qt.DashLine)  # get from palette later
        self._baselineDataItem = self.plot([], [], pen=pen)

    def updateFor(self, timeStep: int):
        timeStep = min(timeStep, self._series.size - 1)
        if timeStep >= 0:
            for i, plot in enumerate(self._dataItems):
                if timeStep <= TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:
                    x = self._times[:timeStep]
                    y = self._series.values[i][:timeStep]
                else:
                    x = self._times[timeStep - TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:timeStep]
                    y = self._series.values[i][timeStep - TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:timeStep]

                plot.setData(x, y)
                self._baselineDataItem.setData(x, [0.5] * len(x))

    def minimumSizeHint(self) -> QSize:
        return QSize(super().minimumSizeHint().width(), 150)

    def sizeHint(self) -> QSize:
        return QSize(super().sizeHint().width(), 150)
