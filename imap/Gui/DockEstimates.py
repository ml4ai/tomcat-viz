from typing import Any, Callable
from PyQt5.QtWidgets import QMainWindow, QScrollArea, QWidget, QPushButton, QVBoxLayout
from PyQt5.Qt import QPalette, QColor

from imap.Gui.EstimatesWidget import EstimatesWidget
from imap.Parser.Estimates import Estimates
from imap.Common.Constants import Constants


class UndockedWidget(QWidget):

    def __init__(self, dockCallback: Callable, legendToggleCallback: Callable, panelToggleCallback: Callable,
                 searchChangeCallback: Callable):
        super().__init__()

        self._dockCallback = dockCallback
        self._legendToggleCallback = legendToggleCallback
        self._panelToggleCallback = panelToggleCallback
        self._searchChangeCallback = searchChangeCallback

        palette = QPalette()
        palette.setColor(QPalette.Active, QPalette.Window, QColor(Constants.Colors.APP_BACKGROUND.value))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.setWindowTitle("Probability Estimates")
        self.setMinimumSize(Constants.MIN_WINDOW_SIZE)

        self._createWidgets()
        self._configureLayout()

    def _createWidgets(self):
        self.estimatesWidget = EstimatesWidget(False)
        self.estimatesWidget.setLegendToggleCallback(self._legendToggleCallback)
        self.estimatesWidget.setPanelToggleCallback(self._panelToggleCallback)
        self.estimatesWidget.setSearchChangeCallback(self._searchChangeCallback)

        self._dockButton = QPushButton("Attach to Main Window")
        self._dockButton.clicked.connect(self._onDockButtonClick)

        self._scrollArea = QScrollArea()
        self._scrollArea.setWidget(self.estimatesWidget)
        self._scrollArea.setWidgetResizable(True)

    def _configureLayout(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self._dockButton)
        mainLayout.addWidget(self._scrollArea)

    def _onDockButtonClick(self, event: Any):
        self._dockCallback()

    def closeEvent(self, event):
        event.accept()
        self._dockCallback()


class DockedWidget(QWidget):

    def __init__(self, undockCallback: Callable, legendToggleCallback: Callable, panelToggleCallback: Callable,
                 searchChangeCallback: Callable):
        super().__init__()

        self._undockCallback = undockCallback
        self._legendToggleCallback = legendToggleCallback
        self._panelToggleCallback = panelToggleCallback
        self._searchChangeCallback = searchChangeCallback

        palette = QPalette()
        palette.setColor(QPalette.Active, QPalette.Window, QColor(Constants.Colors.APP_BACKGROUND.value))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self._createWidgets()
        self._configureLayout()

    def _createWidgets(self):
        self.estimatesWidget = EstimatesWidget()
        self.estimatesWidget.setLegendToggleCallback(self._legendToggleCallback)
        self.estimatesWidget.setPanelToggleCallback(self._panelToggleCallback)
        self.estimatesWidget.setSearchChangeCallback(self._searchChangeCallback)

        self._undockButton = QPushButton("Detach from Main Window")
        self._undockButton.clicked.connect(self._onUndockButtonClick)

        self._scrollArea = QScrollArea()
        self._scrollArea.setWidget(self.estimatesWidget)
        self._scrollArea.setWidgetResizable(True)

    def _configureLayout(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self._undockButton)
        mainLayout.addWidget(self._scrollArea)

    def _onUndockButtonClick(self, event: Any):
        self._undockCallback()


class DockEstimates(QWidget):

    def __init__(self):
        """
        This component has two widgets. One will be docked to a window and the other one won't.
        As they are docked and undocked, we show either its undocked version as a free float window or the other.

        """
        super().__init__()

        self.dockedWidget = DockedWidget(self._onUndock, self._onLegendToggleInDockedWidget,
                                         self._onPanelToggleInDockedWidget, self._onSearchChangeInDockedWidget)
        self._undockedWidget = UndockedWidget(self._onDock, self._onLegendToggleInUndockedWidget,
                                              self._onPanelToggleInUndockedWidget, self._onSearchChangeInUndockedWidget)
        self._lastTimeStepRequested = -1

        self.dock()

    def updateFor(self, timeStep: int):
        self._lastTimeStepRequested = timeStep
        if self.dockedWidget.isVisible():
            self.dockedWidget.estimatesWidget.updateFor(timeStep)
        else:
            self._undockedWidget.estimatesWidget.updateFor(timeStep)

    def loadEstimates(self, estimates: Estimates):
        self.dockedWidget.estimatesWidget.loadEstimates(estimates)
        self._undockedWidget.estimatesWidget.loadEstimates(estimates)

    def dock(self):
        self._onDock()

    def undock(self):
        self._onUndock()

    def close(self):
        self._undockedWidget.close()

    def _onDock(self):
        self.dockedWidget.setVisible(True)
        self._undockedWidget.setVisible(False)
        self.updateFor(self._lastTimeStepRequested)

    def _onUndock(self):
        self.dockedWidget.setVisible(False)
        self._undockedWidget.setVisible(True)
        self.updateFor(self._lastTimeStepRequested)

    def _onLegendToggleInDockedWidget(self, legendIndex: int, timeSeriesIndex: int, groupIndex: int):
        self._undockedWidget.estimatesWidget.toggleLegend(legendIndex, timeSeriesIndex, groupIndex)

    def _onLegendToggleInUndockedWidget(self, legendIndex: int, timeSeriesIndex: int, groupIndex: int):
        self.dockedWidget.estimatesWidget.toggleLegend(legendIndex, timeSeriesIndex, groupIndex)

    def _onPanelToggleInDockedWidget(self, panelIndex: int):
        self._undockedWidget.estimatesWidget.togglePanel(panelIndex)

    def _onPanelToggleInUndockedWidget(self, panelIndex: int):
        self.dockedWidget.estimatesWidget.togglePanel(panelIndex)

    def _onSearchChangeInDockedWidget(self, groupIndex: int, searchQuery: str):
        self._undockedWidget.estimatesWidget.filterPlots(groupIndex, searchQuery)

    def _onSearchChangeInUndockedWidget(self, groupIndex: int, searchQuery: str):
        self.dockedWidget.estimatesWidget.filterPlots(groupIndex, searchQuery)
