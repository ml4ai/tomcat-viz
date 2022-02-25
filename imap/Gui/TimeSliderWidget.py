from typing import Callable
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QStyleOptionSlider, QStyle, QToolButton
from PyQt5.Qt import Qt, QMouseEvent, QCoreApplication, QEvent, QPoint, QTimer

from imap.Gui.Utils import createLabel
from imap.Common.Constants import Constants
from imap.Common.Format import secondsToTime


# class SliderCustom(QSlider):
#
#     def moveBackwards(self):
#         pos = self.style().sliderPositionFromValue(self.minimum(), self.maximum(), 5, 1, False)
#         mousePressEvent = QMouseEvent(QEvent.MouseButtonPress, pos, Qt.LeftButton, Qt.LeftButton,
#                                       Qt.KeyboardModifier.NoModifier)
#         QCoreApplication.sendEvent(self, mousePressEvent)
#
#     def moveForward(self):
#         value = self.value() + 1
#         style = self.style()
#         opt = QStyleOptionSlider()
#         self.initStyleOption(opt)
#
#         # the available space for the handle
#         available = style.pixelMetric(QStyle.PM_SliderSpaceAvailable, opt, self)
#         # the extent of the slider handle
#         sLen = style.pixelMetric(QStyle.PM_SliderLength, opt, self) / 2
#         posX = opt.rect.x() + self.style().sliderPositionFromValue(self.minimum(), self.maximum(), value, available, False) + sLen
#         posY = self.height() / 2
#         print(QPoint(posX, posY))
#         mousePressEvent = QMouseEvent(QEvent.MouseButtonPress, QPoint(posX, posY), Qt.LeftButton, Qt.LeftButton,
#                                       Qt.KeyboardModifier.NoModifier)
#         QCoreApplication.sendEvent(self, mousePressEvent)

    # def mousePressEvent(self, event):
    #     print(event.pos())
    #     if event.button() == Qt.LeftButton and not self.isSliderDown():
    #         opt = QStyleOptionSlider()
    #         self.initStyleOption(opt)
    #         sliderRect = self.style().subControlRect(
    #             QStyle.CC_Slider, opt,
    #             QStyle.SC_SliderHandle, self)
    #         if event.pos() not in sliderRect:
    #             # the mouse is not over the handle, let's move it; this is based
    #             # on the original C++ code that moves the handle when the
    #             # "absolute button" is pressed
    #             grooveRect = self.style().subControlRect(
    #                 QStyle.CC_Slider, opt,
    #                 QStyle.SC_SliderGroove, self)
    #             center = sliderRect.center() - sliderRect.topLeft()
    #             pos = event.pos() - center
    #             if self.orientation() == Qt.Horizontal:
    #                 sliderLength = sliderRect.width()
    #                 sliderMin = grooveRect.x()
    #                 sliderMax = grooveRect.right() - sliderLength + 1
    #                 pos = pos.x()
    #             else:
    #                 sliderLength = sliderRect.height()
    #                 sliderMin = grooveRect.y()
    #                 sliderMax = grooveRect.bottom() - sliderLength + 1
    #                 pos = pos.y()
    #             value = self.style().sliderValueFromPosition(
    #                 self.minimum(), self.maximum(), pos - sliderMin,
    #                                                 sliderMax - sliderMin, opt.upsideDown
    #             )
    #             self.setSliderPosition(value)
    #     super().mousePressEvent(event)


class TimeSliderWidget(QWidget):

    def __init__(self, onValueChangedCallback: Callable):
        super().__init__()

        self._onValueChangedCallback = onValueChangedCallback
        self._playing = False

        self._timer = QTimer()
        self._timer.timeout.connect(self._onForwardClick)

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
        self._timeSlider.valueChanged.connect(self._onValueChange)
        self._playPauseButton = QToolButton()
        self._playPauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self._playPauseButton.setEnabled(False)
        self._playPauseButton.clicked.connect(self._onPlayPause)
        self._rewindButton = QToolButton()
        self._rewindButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self._rewindButton.setEnabled(False)
        self._forwardButton = QToolButton()
        self._forwardButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self._forwardButton.setEnabled(True)
        self._rewindButton.clicked.connect(self._onRewindClick)
        self._forwardButton.clicked.connect(self._onForwardClick)

    def _configureLayout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._playPauseButton)
        layout.addWidget(self._rewindButton)
        layout.addWidget(self._forwardButton)
        layout.addWidget(self._timeSlider)
        layout.addWidget(self._timerLabel)

    def _onValueChange(self, newValue: int):
        self._updateTimerState(newValue)
        self._updateButtonsState(newValue)
        self._updateTimerLabel(newValue)
        self._onValueChangedCallback(newValue)

    def _onPlayPause(self):
        if self._playing:
            self._playPauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self._timer.stop()
        else:
            self._playPauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self._timer.start(self._timeSlider.maximum())

        self._playing = not self._playing

    def _onRewindClick(self):
        self._timeSlider.triggerAction(QSlider.SliderSingleStepSub)

    def _onForwardClick(self):
        self._timeSlider.triggerAction(QSlider.SliderSingleStepAdd)

    def _updateButtonsState(self, timeStep: int):
        if timeStep == 0:
            self._rewindButton.setEnabled(False)
        else:
            self._rewindButton.setEnabled(True)

        if timeStep == self._timeSlider.maximum():
            self._forwardButton.setEnabled(False)
            self._playPauseButton.setEnabled(False)
        else:
            self._forwardButton.setEnabled(True)
            self._playPauseButton.setEnabled(True)

    def _updateTimerState(self, timeStep: int):
        if timeStep == self._timeSlider.maximum() and self._playing:
            self._onPlayPause()

    def _updateTimerLabel(self, timeStep: int):
        self._timerLabel.setText(secondsToTime(timeStep))
