from typing import Dict, List
from pyqtgraph import PlotWidget, mkPen, mkColor, mkBrush
from PyQt5.Qt import Qt, QSize, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QSizePolicy

from imap.Common.Constants import Constants
from imap.Common.Format import secondsToTime
from imap.Parser.Estimates import TimeSeries
from imap.Gui.PlotLegendWidget import PlotLegendWidget


class TimeSeriesPlotWidget(QWidget):
    NUM_VISIBLE_TIME_STEPS = 5
    MARKER_SIZE = 5
    COLOR_PALETTE = [
        "#105ca4",
        "#fe9602",
        "#07ba43",
        "#fe2c02",
        "#855b98",
    ]

    def __init__(self, series: TimeSeries):
        super().__init__()

        self._series = series
        self._times = list(range(series.size))
        self._lastRequestedTimeStep = -1

        self._createWidgets()
        self._configureLayout()
        self._configurePlot()
        self._initializePlot()

    def updateFor(self, timeStep: int):
        self._lastRequestedTimeStep = timeStep
        timeStep = min(timeStep + 1, self._series.size)
        if timeStep >= 0:
            self._plotBaseline(timeStep)

            for i, plot in enumerate(self._dataItems):
                if self._legendWidgets[i].enabled:
                    if timeStep <= TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:
                        x = self._times[:timeStep]
                        y = self._series.values[i][:timeStep]
                    else:
                        x = self._times[timeStep - TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:timeStep]
                        y = self._series.values[i][timeStep - TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:timeStep]

                    plot.setData(x, y)
                else:
                    plot.setData([], [])

    def _createWidgets(self):
        self._plotWidget = PlotWidget()
        self._legendWidgets = []
        if self._series.cardinality > 1:
            for i in range(self._series.cardinality):
                label = self._series.labels[i]
                color = TimeSeriesPlotWidget.COLOR_PALETTE[i % len(TimeSeriesPlotWidget.COLOR_PALETTE)]
                legendWidget = PlotLegendWidget(label, color, i)
                legendWidget.setToggleCalback(self._onLegendToggle)
                self._legendWidgets.append(legendWidget)

    def _configureLayout(self):
        # 3 legends per row
        legendsLayout = QGridLayout()
        legendsLayout.setAlignment(Qt.AlignCenter)
        legendsLayout.setHorizontalSpacing(20)
        row = 0
        for col, legendWidget in enumerate(self._legendWidgets):
            legendsLayout.addWidget(legendWidget, row, col)

            if col > 0 and col % 3 == 0:
                row += 1

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(legendsLayout)
        mainLayout.addWidget(self._plotWidget)

    def _configurePlot(self):
        self._plotWidget.setBackground("white")
        self._plotWidget.setYRange(0, 1)
        self._plotWidget.setMouseEnabled(x=False, y=False)
        self._plotWidget.setMinimumHeight(150)
        self._plotWidget.setMaximumHeight(150)
        self._plotWidget.centralWidget.hideButtons()
        self._plotWidget.setTitle(self._series.name)
        self._adjustTickLabels()

    def _initializePlot(self):
        # Baseline
        pen = mkPen(color=mkColor("red"), width=1, style=Qt.DashLine)  # get from palette later
        self._baselineDataItem = self._plotWidget.plot([], [], pen=pen)

        # Other series
        self._dataItems = []
        for i in range(self._series.cardinality):
            pen = mkPen(color=mkColor(TimeSeriesPlotWidget.COLOR_PALETTE[i]), width=2)
            brush = mkBrush(color=mkColor(TimeSeriesPlotWidget.COLOR_PALETTE[i]))
            self._dataItems.append(
                self._plotWidget.plot([], [], pen=pen, brush=brush, symbol='s',
                                      symbolSize=TimeSeriesPlotWidget.MARKER_SIZE,
                                      symbolPen=pen, symbolBrush=brush))

    def _adjustTickLabels(self):
        ax = self._plotWidget.getAxis('bottom')
        ax.setTicks([[(v, secondsToTime(v)) for v in self._times]])

    def _plotBaseline(self, timeStep: int):
        if timeStep <= TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:
            x = self._times[:timeStep]
        else:
            x = self._times[timeStep - TimeSeriesPlotWidget.NUM_VISIBLE_TIME_STEPS:timeStep]

        self._baselineDataItem.setData(x, [0.5] * len(x))

    def _onLegendToggle(self, index: int):
        self.updateFor(self._lastRequestedTimeStep)
