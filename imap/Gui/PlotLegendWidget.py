from typing import Any, Callable
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGraphicsOpacityEffect
from PyQt5.Qt import Qt, QSize

from imap.Common.Constants import Constants
from imap.Gui.Utils import createLabel, createEmptyWidget


class PlotLegendWidget(QWidget):
    MARKER_SIZE = 10

    def __init__(self, label: str, color: str, index: int):
        super().__init__()

        self._label = label
        self._color = color
        self._index = index
        self._toggleCallback = None

        self.enabled = True
        self.mousePressEvent = self._toggleLegend

        self._createWidgets()
        self._configureLayout()

    def setToggleCalback(self, callback: Callable):
        self._toggleCallback = callback

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

    def _toggleLegend(self, event: Any):
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

        if self._toggleCallback is not None:
            self._toggleCallback(self._index)

