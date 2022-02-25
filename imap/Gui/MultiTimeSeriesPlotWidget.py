from typing import Callable, List

from PyQt5.QtWidgets import QVBoxLayout, QLineEdit
from PyQt5.QtWidgets import QWidget

from imap.Common.Constants import Constants
from imap.Gui.TimeSeriesPlotWidget import TimeSeriesPlotWidget
from imap.Gui.Utils import createHorizontalSeparator
from imap.Parser.Estimates import TimeSeries


class MultiTimeSeriesPlotWidget(QWidget):

    def __init__(self, timeSeries: List[TimeSeries], groupIndex: int, num_visible_time_steps: int = 5):
        super().__init__()

        self._timeSeries = timeSeries
        self._groupIndex = groupIndex
        self._num_visible_time_steps = num_visible_time_steps

        self._plotWidgets = []
        self._onLegendToggleCallback = None
        self._onSearchChangeCallback = None
        self._invokeSearchChangeCallback = True

        self._createWidgets()
        self._configureLayout()

    def _createWidgets(self):
        self._searchField = QLineEdit()
        self._searchField.setPlaceholderText("Filter by title")
        self._searchField.textChanged.connect(self._onSearchChange)
        self._searchField.setStyleSheet(
            f"background-color: {Constants.Colors.SEARCH_FIELD_BACKGROUND.value}; border-radius: 5px;")
        self._searchField.setFont(Constants.Font.SMALL_REGULAR.value)

        for i, series in enumerate(self._timeSeries):
            plotWidget = TimeSeriesPlotWidget(series, i, self._num_visible_time_steps)
            plotWidget.setLegendToggleCallback(self._onLegendToggle)
            self._plotWidgets.append(plotWidget)

    def _configureLayout(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self._searchField)
        mainLayout.addWidget(createHorizontalSeparator())
        for i, plotWidget in enumerate(self._plotWidgets):
            mainLayout.addWidget(plotWidget)
            # if i < len(self._plotWidgets) - 1:
            #     mainLayout.addWidget(createHorizontalSeparator())
        mainLayout.addStretch()

    def updateFor(self, timeStep: int):
        for plotWidget in self._plotWidgets:
            plotWidget.updateFor(timeStep)

    def setLegendToggleCallback(self, callback: Callable):
        self._onLegendToggleCallback = callback

    def setSearchChangeCallback(self, callback: Callable):
        self._onSearchChangeCallback = callback

    def toggleLegend(self, legendIndex: int, timeSeriesIndex: int):
        self._plotWidgets[timeSeriesIndex].toggleLegend(legendIndex)

    def filterPlots(self, searchQuery: str):
        self._invokeSearchChangeCallback = False
        self._searchField.setText(searchQuery)

    def _onSearchChange(self):
        searchQuery = self._searchField.text().lower()
        for i, plotWidget in enumerate(self._plotWidgets):
            if searchQuery not in self._timeSeries[i].name.lower():
                plotWidget.setVisible(False)
            else:
                plotWidget.setVisible(True)
        if self._invokeSearchChangeCallback and self._onSearchChangeCallback is not None:
            self._onSearchChangeCallback(self._groupIndex, self._searchField.text())
        self._invokeSearchChangeCallback = True

    def _onLegendToggle(self, legendIndex: int, timeSeriesIndex: int):
        if self._onLegendToggleCallback is not None:
            self._onLegendToggleCallback(legendIndex, timeSeriesIndex, self._groupIndex)
