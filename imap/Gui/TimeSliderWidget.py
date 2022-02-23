from typing import Callable
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider
from PyQt5.Qt import Qt

from imap.Gui.Utils import createLabel
from imap.Common.Constants import Constants
from imap.Common.Format import secondsToTime


class TimeSliderWidget(QWidget):

    def __init__(self, onValueChangedCallback: Callable):
        super().__init__()

        self._onValueChangedCallback = onValueChangedCallback

        self._createWidgets()
        self._configureLayout()

    def setTimeSteps(self, timeSteps: int):
        self._timeSlider.setRange(0, timeSteps - 1)

    def reset(self):
        self._timeSlider.setValue(0)

    def setEnabled(self, enabled: bool):
        self._timeSlider.setEnabled(enabled)
        if enabled:
            self._updateButtonsState(self._timeSlider.value())
        else:
            self._rewindButton.setEnabled(False)
            self._forwardButton.setEnabled(False)

    def value(self):
        return self._timeSlider.value()

    def _createWidgets(self):
        self._timerLabel = createLabel("00:00", Constants.Font.SMALL_REGULAR.value, alignment=Qt.AlignCenter)
        self._timeSlider = QSlider(Qt.Horizontal)
        self._timeSlider.setSingleStep(1)
        self._timeSlider.setTracking(True)
        self._timeSlider.valueChanged.connect(self._onValueChange)
        self._rewindButton = QPushButton("-")
        self._rewindButton.setEnabled(False)
        self._forwardButton = QPushButton("+")
        self._forwardButton.setEnabled(False)
        self._rewindButton.clicked.connect(self._onRewindClick)
        self._forwardButton.clicked.connect(self._onForwardClick)

    def _configureLayout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._rewindButton)
        layout.addWidget(self._forwardButton)
        layout.addWidget(self._timeSlider)
        layout.addWidget(self._timerLabel)

    def _onValueChange(self, newValue: int):
        self._updateButtonsState(newValue)
        self._updateTimerLabel(newValue)
        self._onValueChangedCallback(newValue)

    def _onRewindClick(self):
        newSliderValue = self._timeSlider.value() - 1
        self._timeSlider.setValue(newSliderValue)

    def _onForwardClick(self):
        newSliderValue = self._timeSlider.value() + 1
        self._timeSlider.setValue(newSliderValue)

    def _updateButtonsState(self, timeStep: int):
        if timeStep == 0:
            self._rewindButton.setEnabled(False)
        else:
            self._rewindButton.setEnabled(True)

        if timeStep == self._timeSlider.maximum():
            self._forwardButton.setEnabled(False)
        else:
            self._forwardButton.setEnabled(True)

    def _updateTimerLabel(self, timeStep: int):
        self._timerLabel.setText(secondsToTime(timeStep))
