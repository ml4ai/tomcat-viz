from PyQt5.QtWidgets import QMainWindow, QWidget, QScrollArea, QFrame
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QLayout
from PyQt5.QtWidgets import QCheckBox, QSlider, QFileDialog
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
from imap.Gui.PlayerPanelWidget import PlayerPanelWidget

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

        self._boldLabelFont = QFont("Arial", 14, QFont.Bold)
        self._regularLabelFont = QFont("Arial", 14)

        self._createWidgets()
        self._configureLayout()
        self._createMenu()

        self._scores = np.array([])
        self._loadDefaultMap()

        self._trial = None

    def _createWidgets(self):
        # Trial Info
        self._trialLabel = createLabel("", self._regularLabelFont)
        self._teamLabel = createLabel("", self._regularLabelFont)

        # Game Info
        self._scoreLabel = createLabel("0", self._regularLabelFont)
        self._perturbationCheckbox = QCheckBox()
        self._perturbationCheckbox.setEnabled(False)

        # Player Info
        self._redPanel = PlayerPanelWidget(Constants.Colors.RED_PLAYER.value)
        self._greenPanel = PlayerPanelWidget(Constants.Colors.GREEN_PLAYER.value)
        self._bluePanel = PlayerPanelWidget(Constants.Colors.BLUE_PLAYER.value)

        # Map
        mapWidth = int(self.width() * MainWindow.LEFT_PANEL_PROP / 100)
        mapHeight = int(self.height() * MainWindow.MAP_HEIGHT_PROP / 100)
        self._mapWidget = MapWidget(mapWidth, mapHeight)

        # Timer
        self._timerLabel = createLabel("00:00", self._regularLabelFont, alignment=Qt.AlignCenter)
        self._timeSlider = QSlider(Qt.Horizontal)
        self._timeSlider.setEnabled(False)
        self._timeSlider.setRange(0, 899)
        self._timeSlider.setSingleStep(1)
        self._timeSlider.valueChanged.connect(self._updateTimerAction)

        self._chatWidget = SpeechWidget()
        self._estimatesWidget = EstimatesWidget()

    def _configureLayout(self):
        sidePanelLayout = QHBoxLayout()

        leftPanelLayout = QVBoxLayout()
        rightPanelLayout = QVBoxLayout()

        sidePanelLayout.addLayout(leftPanelLayout, MainWindow.LEFT_PANEL_PROP)
        sidePanelLayout.addLayout(rightPanelLayout, 100 - MainWindow.LEFT_PANEL_PROP)

        # Widgets on the left side of the window
        self._createTrialInfoPanel(leftPanelLayout)
        self._createGameInfoPanel(leftPanelLayout)
        self._createMapPanel(leftPanelLayout)
        self._createSliderPanel(leftPanelLayout)

        # Widgets on the right side of the window
        rightPanelLayout.addWidget(self._chatWidget, 50)
        scrollArea = QScrollArea()
        scrollArea.setWidget(self._estimatesWidget)
        scrollArea.setWidgetResizable(True)
        rightPanelLayout.addWidget(scrollArea, 50)

        self._centralWidget.setLayout(sidePanelLayout)

    def _createTrialInfoPanel(self, parentLayout: QLayout):
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignLeft)
        layout.setFormAlignment(Qt.AlignLeft)
        layout.addRow(createLabel("Trial:", self._boldLabelFont), self._trialLabel)
        layout.addRow(createLabel("Team:", self._boldLabelFont), self._teamLabel)
        parentLayout.addLayout(layout, 5)

    def _createGameInfoPanel(self, parentLayout: QLayout):
        layout = QHBoxLayout()
        centerInfoLayout = QVBoxLayout()

        # Score and Perturbation
        upper_info = QHBoxLayout()
        upper_info.setAlignment(Qt.AlignCenter)
        score_layout = QFormLayout()
        score_layout.addRow(createLabel("Score:", self._boldLabelFont), self._scoreLabel)
        perturbation_layout = QFormLayout()
        perturbation_layout.addRow(createLabel("Perturbation:", self._boldLabelFont), self._perturbationCheckbox)
        upper_info.addLayout(score_layout)
        upper_info.addLayout(perturbation_layout)
        centerInfoLayout.addLayout(upper_info)

        # Player IDs
        # self._createPlayerInfoPanel(centerInfoLayout)
        bottom_info_layout = QHBoxLayout()
        bottom_info_layout.addWidget(self._redPanel)
        bottom_info_layout.addWidget(self._greenPanel)
        bottom_info_layout.addWidget(self._bluePanel)
        centerInfoLayout.addLayout(bottom_info_layout)

        layout.addWidget(QWidget(), 20)
        layout.addLayout(centerInfoLayout, 60)
        layout.addWidget(QWidget(), 20)

        parentLayout.addLayout(layout, 5)

    def _createMapPanel(self, parentLayout: QLayout):
        parentLayout.addWidget(self._mapWidget, MainWindow.MAP_HEIGHT_PROP)

    def _createSliderPanel(self, parentLayout: QLayout):
        layout = QHBoxLayout()
        layout.addWidget(self._timeSlider, 95)
        layout.addWidget(self._timerLabel, 5)
        parentLayout.addLayout(layout, 5)

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
    def _updateTimerAction(self, value):
        self._updateHeaderInfo(value)

        # Update custom widgets
        self._mapWidget.updateFor(value)
        self._chatWidget.updateFor(value)
        self._estimatesWidget.updateFor(value)

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
        self._timeSlider.setValue(0)
        self._timeSlider.setEnabled(True)
        self._initializeHeaderInfo()
        self._mapWidget.loadTrial(self._trial)
        self._chatWidget.loadTrial(self._trial)
        self._dumpAction.setEnabled(True)

    def _initializeHeaderInfo(self):
        self._trialLabel.setText(self._trial.metadata["trial_number"])
        self._teamLabel.setText(self._trial.metadata["team_number"])
        self._redPanel.setName(self._trial.metadata["red_id"])
        self._greenPanel.setName(self._trial.metadata["green_id"])
        self._bluePanel.setName(self._trial.metadata["blue_id"])

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
        self._timerLabel.setText(secondsToTime(timeStep))
        self._scoreLabel.setText(f"{self._trial.scores[timeStep]}")
        self._updateActions(timeStep)

    def _updateActions(self, timeStep: int):
        panels = [self._redPanel, self._greenPanel, self._bluePanel]
        for i, panel in enumerate(panels):
            action = self._trial.playersActions[i][timeStep]
            panel.setAction(action)

    def createWidget(self, color: str):
        widget = QWidget()
        widget.setStyleSheet(f"background-color:{color};")
        widget.setFixedSize(20, 20)
        return widget
