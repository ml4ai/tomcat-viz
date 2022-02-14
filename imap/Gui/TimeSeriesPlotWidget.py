from typing import Dict, List
from pyqtgraph import PlotWidget, mkPen
from PyQt5.QtCore import Qt

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

        self.setMinimumHeight(150)

    def _configure(self):
        self.setBackground("white")
        self.setYRange(0, 1)

        # self.palette = ...

    def _initializePlot(self):
        self._plots = []
        for _ in self._series.values:
            pen = mkPen(color=(0, 0, 255), width=2)  # get from palette later
            self._plots.append(self.plot([], [], pen=pen))
            break

        # Baseline
        pen = mkPen(color=(255, 0, 0), width=1, style=Qt.DashLine)  # get from palette later
        self._baselinePlot = self.plot([], [], pen=pen)

    def updateFor(self, timeStep: int):
        timeStep = min(timeStep, self._series.size - 1)
        if timeStep >= 0:
            for i, plot in enumerate(self._plots):
                if timeStep <= TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:
                    x = self._times[:timeStep]
                    y = self._series.values[i][:timeStep]
                else:
                    x = self._times[timeStep - TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:timeStep]
                    y = self._series.values[i][timeStep - TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:timeStep]

                plot.setData(x, y)
                self._baselinePlot.setData(x, [0.5] * len(x))
