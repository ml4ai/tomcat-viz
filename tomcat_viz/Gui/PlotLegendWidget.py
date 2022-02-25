from typing import Any, Callable
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGraphicsOpacityEffect
from PyQt5.Qt import Qt, QSize

from tomcat_viz.Common.Constants import Constants
from tomcat_viz.Gui.Utils import createLabel, createEmptyWidget


class PlotLegendWidget(QWidget):
    MARKER_SIZE = 10

    def __init__(self, label: str, color: str, legendIndex: int):
        super().__init__()

        self._label = label
        self._color = color
        self._legendIndex = legendIndex
        self._toggleCallback = None

        self.enabled = True
        self.mousePressEvent = self.toggleLegend

        self._createWidgets()
        self._configureLayout()

    def setToggleCalback(self, callback: Callable):
        self._toggleCallback = callback

    def toggleLegend(self, event: Any = None):
        self.enabled = not self.enabled
        opacity_effect = QGraphicsOpacityEffect()
        if self.enabled:
            self._markerWidget.setStyleSheet(f"background-color: {self._color}")
            self._legendLabel.setStyleSheet(f"color: {self._color}")
            opacity_effect.setOpacity(1)
        else:
            self._markerWidget.setStyleSheet(f"background-color: #BFBFBF")
            self._legendLabel.setStyleSheet(f"color: #BFBFBF")
            opacity_effect.setOpacity(0.7)

        self.setGraphicsEffect(opacity_effect)

        if event is not None and self._toggleCallback is not None:
            # Clicking a button will trigger a callback so that the same event can be replicated in another component
            # that also presents the same set of plots
            self._toggleCallback(self._legendIndex)

    def _createWidgets(self):
        self._markerWidget = createEmptyWidget(self._color,
                                               QSize(PlotLegendWidget.MARKER_SIZE, PlotLegendWidget.MARKER_SIZE))
        self._legendLabel = createLabel(self._label, Constants.Font.SMALL_REGULAR.value, self._color, Qt.AlignLeft)
        self._legendLabel.adjustSize()

    def _configureLayout(self):
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self._markerWidget)
        mainLayout.addWidget(self._legendLabel)
