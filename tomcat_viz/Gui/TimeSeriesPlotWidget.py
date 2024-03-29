from typing import Callable

from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from pyqtgraph import PlotWidget, mkPen, mkColor, mkBrush

from tomcat_viz.Common.Constants import Constants
from tomcat_viz.Common.Format import secondsToTime
from tomcat_viz.Gui.PlotLegendWidget import PlotLegendWidget
from tomcat_viz.Parser.Estimates import TimeSeries


class TimeSeriesPlotWidget(QWidget):
    MARKER_SIZE = 5
    LEGENDS_PER_ROW = 2
    COLOR_PALETTE = [
        "#105ca4",
        "#fe9602",
        "#07ba43",
        "#fe2c02",
        "#855b98",
    ]

    def __init__(self, series: TimeSeries, timeSeriesIndex: int, num_visible_time_steps: int = 5):
        super().__init__()

        self._series = series
        self._times = list(range(series.size))
        self._lastRequestedTimeStep = -1
        self._timeSeriesIndex = timeSeriesIndex
        self._num_visible_time_steps = num_visible_time_steps
        self._legendToggleCallback = None

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
                    if timeStep <= self._num_visible_time_steps:
                        x = self._times[:timeStep]
                        y = self._series.values[i][:timeStep]
                    else:
                        x = self._times[timeStep - self._num_visible_time_steps:timeStep]
                        y = self._series.values[i][timeStep - self._num_visible_time_steps:timeStep]

                    plot.setData(x, y)
                else:
                    plot.setData([], [])

    def setLegendToggleCallback(self, callback: Callable):
        self._legendToggleCallback = callback

    def toggleLegend(self, legendIndex: int):
        self._legendWidgets[legendIndex].toggleLegend()

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
        legendsLayout = QGridLayout()
        legendsLayout.setContentsMargins(0, 0, 0, 0)
        legendsLayout.setAlignment(Qt.AlignCenter)
        legendsLayout.setHorizontalSpacing(20)
        row = 0
        col = 0
        for legendWidget in self._legendWidgets:
            legendsLayout.addWidget(legendWidget, row, col)
            col += 1

            if col > 0 and col % TimeSeriesPlotWidget.LEGENDS_PER_ROW == 0:
                col = 0
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

        # self._plotWidget.scene().sigMouseClicked.connect(self._onClick)

    # def _onClick(self, event):
    #     if self._plotWidget.sceneBoundingRect().contains(event._scenePos):
    #         mousePoint = self._plotWidget.plotItem.vb.mapSceneToView(event._scenePos)
    #         dataIndex = int(mousePoint.x())
    #         # if index > 0 and index < self._num_visible_time_steps:
    #             # label.setText(
    #             #     "<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (
    #             #         mousePoint.x(), data1[index], data2[index]))

    def _adjustTickLabels(self):
        ax = self._plotWidget.getAxis('bottom')
        ax.setTicks([[(v, secondsToTime(v)) for v in self._times]])
        ax.setTickFont(Constants.Font.SMALL_REGULAR.value)
        ay = self._plotWidget.getAxis('left')
        ay.setTickFont(Constants.Font.SMALL_REGULAR.value)

    def _plotBaseline(self, timeStep: int):
        if timeStep <= self._num_visible_time_steps:
            x = self._times[:timeStep]
        else:
            x = self._times[timeStep - self._num_visible_time_steps:timeStep]

        self._baselineDataItem.setData(x, [0.5] * len(x))

    def _onLegendToggle(self, legendIndex: int):
        self.updateFor(self._lastRequestedTimeStep)
        if self._legendToggleCallback is not None:
            self._legendToggleCallback(legendIndex, self._timeSeriesIndex)
