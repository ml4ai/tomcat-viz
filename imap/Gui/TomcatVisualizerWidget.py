from PyQt5.QtWidgets import QMainWindow, QWidget, QScrollArea, QFrame
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QLayout
from PyQt5.QtWidgets import QCheckBox, QSlider, QFileDialog, QPushButton, QSplitter
from PyQt5.Qt import Qt, QFont, QMenu, QAction, QPalette, QColor

from imap.Gui.Utils import createLabel
from imap.Gui.TextMessageWidget import TextMessageWidget
from imap.Gui.EstimatesWidget import EstimatesWidget
from imap.Common.Format import secondsToTime
from imap.Common.Constants import Constants
from imap.Gui.MapWidget import MapWidget
from imap.Parser.Map import Map
from imap.Parser.Trial import Trial
from imap.Parser.Estimates import Estimates
from imap.Gui.HeaderWidget import HeaderWidget
from imap.Gui.TimeSliderWidget import TimeSliderWidget

import json
import numpy as np
from pkg_resources import resource_stream
import codecs


class TomcatVisualizerWidget(QWidget):
    LEFT_PANEL_PROP = 80
    MAP_HEIGHT_PROP = 80

    def __init__(self):
        super().__init__()

        self.setMinimumSize(1800, 1020)
        palette = QPalette()
        palette.setColor(QPalette.Active, QPalette.Window, QColor(Constants.Colors.APP_BACKGROUND.value))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self._createWidgets()
        self._configureLayout()

        self._loadDefaultMap()

        self._trial = None

    def loadTrialFromMetadata(self, filepath: str):
        if filepath != "":
            with open(filepath, "r") as f:
                self._trial = Trial(self._map)
                self._trial.parse(f)
            self._initializeTrial()
            return True

        return False

    def loadTrialFromPackage(self, filepath: str):
        if filepath != "":
            self._trial = Trial(self._map)
            self._trial.load(filepath)
            self._initializeTrial()
            return True

        return False

    def dumpTrial(self, filepath: str):
        if filepath != "":
            self._trial.save(filepath)

    def loadEstimates(self, filepath: str):
        if filepath != "":
            self._estimatesWidget.loadEstimates(Estimates(filepath))

    def _createWidgets(self):
        self._headerPanel = HeaderWidget()

        mapWidth = int(self.width() * TomcatVisualizerWidget.LEFT_PANEL_PROP / 100)
        mapHeight = int(self.height() * TomcatVisualizerWidget.MAP_HEIGHT_PROP / 100)
        self._mapWidget = MapWidget(mapWidth, mapHeight)

        self._timeSlider = TimeSliderWidget(self._onTimeStepChange)
        self._timeSlider.setEnabled(False)

        self._chatHeaderLabel = createLabel("Chat Messages", Constants.Font.SMALL_BOLD.value, Qt.AlignLeft)
        self._chatWidget = TextMessageWidget()

        self._estimatesHeaderLabel = createLabel("Probability Estimates", Constants.Font.SMALL_BOLD.value, "black",
                                                 Qt.AlignLeft)
        self._estimatesWidget = EstimatesWidget()

    def _configureLayout(self):
        mainLayout = QHBoxLayout(self)

        leftPanelLayout = QVBoxLayout()
        leftPanelLayout.addWidget(self._headerPanel, 17)
        leftPanelLayout.addWidget(self._mapWidget, TomcatVisualizerWidget.MAP_HEIGHT_PROP)
        leftPanelLayout.addWidget(self._timeSlider, 3)

        chatLayout = QVBoxLayout()
        chatLayout.setContentsMargins(0, 0, 0, 10)
        chatLayout.addWidget(self._chatHeaderLabel)
        chatLayout.addWidget(self._chatWidget)
        chatPanelWidget = QWidget()
        chatPanelWidget.setLayout(chatLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(self._estimatesWidget)
        scrollArea.setWidgetResizable(True)
        estimatesLayout = QVBoxLayout()
        estimatesLayout.setContentsMargins(0, 0, 0, 0)
        estimatesLayout.addWidget(self._estimatesHeaderLabel)
        estimatesLayout.addWidget(scrollArea)
        estimatesPanelWidget = QWidget()
        estimatesPanelWidget.setLayout(estimatesLayout)

        rightPanelSplitter = QSplitter(Qt.Vertical)
        rightPanelSplitter.addWidget(chatPanelWidget)
        rightPanelSplitter.addWidget(estimatesPanelWidget)

        mainLayout.addLayout(leftPanelLayout, TomcatVisualizerWidget.LEFT_PANEL_PROP)
        mainLayout.addWidget(rightPanelSplitter, 100 - TomcatVisualizerWidget.LEFT_PANEL_PROP)
        mainLayout.setStretch(0, 0)
        mainLayout.setStretch(1, 1)

    def _onTimeStepChange(self, newTimeStep: int):
        self._updateHeaderInfo(newTimeStep)
        self._mapWidget.updateFor(newTimeStep)
        self._chatWidget.updateFor(newTimeStep)
        self._estimatesWidget.updateFor(newTimeStep)

    def _initializeTrial(self):
        self._timeSlider.setTimeSteps(self._trial.timeSteps)
        self._timeSlider.reset()
        self._timeSlider.setEnabled(True)

        self._initializeHeaderInfo()
        self._mapWidget.loadTrial(self._trial)
        self._chatWidget.loadTrial(self._trial)

    def _initializeHeaderInfo(self):
        self._headerPanel.setTrialNumber(self._trial.metadata["trial_number"])
        self._headerPanel.setTeamNumber(self._trial.metadata["team_number"])
        self._headerPanel.setRedPlayerName(self._trial.metadata["red_id"])
        self._headerPanel.setGreenPlayerName(self._trial.metadata["green_id"])
        self._headerPanel.setBluePlayerName(self._trial.metadata["blue_id"])
        self._updateHeaderInfo(0)

    def _loadDefaultMap(self):
        objects_resource = resource_stream("imap.Resources.Maps", "Saturn_2.6_3D_sm_v1.0.json")
        utf8_reader = codecs.getreader("utf-8")
        jsonMap = json.load(utf8_reader(objects_resource))
        self._map = Map()
        self._map.parse(jsonMap)
        self._mapWidget.loadMap(self._map)

    def _updateHeaderInfo(self, timeStep: int):
        self._headerPanel.setScore(self._trial.scores[timeStep])
        if self._trial.activeBlackout[timeStep]:
            self._headerPanel.showBlackout()
        else:
            self._headerPanel.hideBlackout()
        self._headerPanel.setRedPlayerAction(self._trial.playersActions[Constants.Player.RED.value][timeStep])
        self._headerPanel.setGreenPlayerAction(self._trial.playersActions[Constants.Player.GREEN.value][timeStep])
        self._headerPanel.setBluePlayerAction(self._trial.playersActions[Constants.Player.BLUE.value][timeStep])
        self._headerPanel.setRedPlayerEquippedItem(
            self._trial.playersEquippedItems[Constants.Player.RED.value][timeStep])
        self._headerPanel.setGreenPlayerEquippedItem(
            self._trial.playersEquippedItems[Constants.Player.GREEN.value][timeStep])
        self._headerPanel.setBluePlayerEquippedItem(
            self._trial.playersEquippedItems[Constants.Player.BLUE.value][timeStep])

    def createWidget(self, color: str):
        widget = QWidget()
        widget.setStyleSheet(f"background-color:{color};")
        widget.setFixedSize(20, 20)
        return widget
