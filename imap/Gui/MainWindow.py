from PyQt5.QtWidgets import QMainWindow, QWidget, QScrollArea, QFrame
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QLayout
from PyQt5.QtWidgets import QCheckBox, QSlider, QFileDialog, QPushButton
from PyQt5.Qt import Qt, QFont, QMenu, QAction

from imap.Gui.Utils import createLabel
from imap.Gui.SpeechWidget import SpeechWidget
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


class MainWindow(QMainWindow):
    LEFT_PANEL_PROP = 80
    MAP_HEIGHT_PROP = 80

    def __init__(self):
        super().__init__()

        self.setWindowTitle('ToMCAT Visualizer')
        self.setFixedSize(1800, 1000)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)

        self._createWidgets()
        self._configureLayout()
        self._createMenu()

        self._loadDefaultMap()

        self._trial = None

    def _createWidgets(self):
        self._headerPanel = HeaderWidget()

        mapWidth = int(self.width() * MainWindow.LEFT_PANEL_PROP / 100)
        mapHeight = int(self.height() * MainWindow.MAP_HEIGHT_PROP / 100)
        self._mapWidget = MapWidget(mapWidth, mapHeight)

        self._timeSlider = TimeSliderWidget(self._onTimeStepChange)
        self._timeSlider.setEnabled(False)

        self._chatWidget = SpeechWidget()
        self._estimatesWidget = EstimatesWidget()

    def _configureLayout(self):
        mainLayout = QHBoxLayout(self._centralWidget)

        leftPanelLayout = QVBoxLayout()
        leftPanelLayout.addWidget(self._headerPanel, 15)
        leftPanelLayout.addWidget(self._mapWidget, MainWindow.MAP_HEIGHT_PROP)
        leftPanelLayout.addWidget(self._timeSlider, 5)

        rightPanelLayout = QVBoxLayout()
        rightPanelLayout.addWidget(self._chatWidget, 50)
        scrollArea = QScrollArea()
        scrollArea.setWidget(self._estimatesWidget)
        scrollArea.setWidgetResizable(True)
        rightPanelLayout.addWidget(scrollArea, 50)

        mainLayout.addLayout(leftPanelLayout, MainWindow.LEFT_PANEL_PROP)
        mainLayout.addLayout(rightPanelLayout, 100 - MainWindow.LEFT_PANEL_PROP)

    def _createMenu(self):
        self._createTrialMenu()
        self._createEstimatesMenu()

    def _createTrialMenu(self):
        menuBar = self.menuBar()
        trialMenu = QMenu("&Trial", self)

        # Load options
        loadMenu = QMenu("&Load", self)
        loadFromMetadataAction = QAction("&From Metadata...", self)
        loadFromPackageAction = QAction("&From Package...", self)
        loadFromMetadataAction.triggered.connect(self._loadTrialFromMetadataAction)
        loadFromPackageAction.triggered.connect(self._loadTrialFromPackageAction)
        loadMenu.addAction(loadFromMetadataAction)
        loadMenu.addAction(loadFromPackageAction)
        trialMenu.addMenu(loadMenu)
        menuBar.addMenu(trialMenu)

        # Dump option
        self._dumpAction = QAction("&Dump...", self)
        self._dumpAction.setEnabled(False)
        self._dumpAction.triggered.connect(self._dumpTrialAction)
        trialMenu.addAction(self._dumpAction)

    def _createEstimatesMenu(self):
        menuBar = self.menuBar()
        trialMenu = QMenu("&Estimates", self)

        # Load options
        loadAction = QAction("&Load...", self)
        loadAction.triggered.connect(self._loadEstimatesAction)
        trialMenu.addAction(loadAction)
        menuBar.addMenu(trialMenu)

    # Actions
    def _onTimeStepChange(self, newTimeStep: int):
        self._updateHeaderInfo(newTimeStep)
        self._mapWidget.updateFor(newTimeStep)
        self._chatWidget.updateFor(newTimeStep)
        self._estimatesWidget.updateFor(newTimeStep)

    def _loadTrialFromMetadataAction(self, value):
        filepath = QFileDialog.getOpenFileName(self, "Select Metadata File", ".", "Metadata File (*.metadata)")[0]
        if filepath != "":
            with open(filepath, "r") as f:
                self._trial = Trial(self._map)
                self._trial.parse(f)
            self._initializeTrial()

    def _loadTrialFromPackageAction(self, value):
        filepath = QFileDialog.getOpenFileName(self, "Select Package File", ".", "Package File (*.pkl)")[0]
        if filepath != "":
            self._trial = Trial(self._map)
            self._trial.load(filepath)
            self._initializeTrial()

    def _dumpTrialAction(self, value):
        filepath = QFileDialog.getSaveFileName(self, "Save Package File", ".", "Package File (*.pkl)")[0]
        if filepath != "":
            self._trial.save(filepath)

    def _initializeTrial(self):
        self._timeSlider.setTimeSteps(self._trial.timeSteps)
        self._timeSlider.reset()
        self._timeSlider.setEnabled(True)

        self._initializeHeaderInfo()
        self._mapWidget.loadTrial(self._trial)
        self._chatWidget.loadTrial(self._trial)
        self._dumpAction.setEnabled(True)

    def _initializeHeaderInfo(self):
        self._headerPanel.setTrialNumber(self._trial.metadata["trial_number"])
        self._headerPanel.setTeamNumber(self._trial.metadata["team_number"])
        self._headerPanel.setRedPlayerName(self._trial.metadata["red_id"])
        self._headerPanel.setGreenPlayerName(self._trial.metadata["green_id"])
        self._headerPanel.setBluePlayerName(self._trial.metadata["blue_id"])
        self._updateHeaderInfo(0)

    def _loadDefaultMap(self):
        objects_resource = resource_stream("imap.Resources.Maps", "Saturn_2.1_3D_sm_v1.0.json")
        utf8_reader = codecs.getreader("utf-8")
        jsonMap = json.load(utf8_reader(objects_resource))
        self._map = Map()
        self._map.parse(jsonMap)
        self._mapWidget.loadMap(self._map)

    def _loadEstimatesAction(self):
        filepath = QFileDialog.getOpenFileName(self, "Select Estimates File", ".", "Package File (*.json)")[0]
        if filepath != "":
            self._estimatesWidget.loadEstimates(Estimates(filepath))

    def _updateHeaderInfo(self, timeStep: int):
        self._headerPanel.setScore(self._trial.scores[timeStep])
        if self._trial.activeBlackout[timeStep]:
            self._headerPanel.showBlackout()
        else:
            self._headerPanel.hideBlackout()
        self._headerPanel.setRedPlayerAction(self._trial.playersActions[Constants.Player.RED.value][timeStep])
        self._headerPanel.setGreenPlayerAction(self._trial.playersActions[Constants.Player.GREEN.value][timeStep])
        self._headerPanel.setBluePlayerAction(self._trial.playersActions[Constants.Player.BLUE.value][timeStep])

    def createWidget(self, color: str):
        widget = QWidget()
        widget.setStyleSheet(f"background-color:{color};")
        widget.setFixedSize(20, 20)
        return widget
