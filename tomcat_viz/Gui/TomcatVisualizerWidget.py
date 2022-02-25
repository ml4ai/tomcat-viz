from PyQt5.Qt import Qt, QPalette, QColor
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QWidget

from tomcat_viz.Common.Constants import Constants
from tomcat_viz.Gui.DockEstimates import DockEstimates
from tomcat_viz.Gui.HeaderWidget import HeaderWidget
from tomcat_viz.Gui.MapWidget import MapWidget
from tomcat_viz.Gui.SpeechTranscriptionWidget import SpeechTranscriptionWidget
from tomcat_viz.Gui.ChatWidget import ChatWidget
from tomcat_viz.Gui.TimeSliderWidget import TimeSliderWidget
from tomcat_viz.Gui.Utils import createLabel
from tomcat_viz.Parser.Estimates import Estimates
from tomcat_viz.Parser.Trial import Trial


class TomcatVisualizerWidget(QWidget):
    LEFT_PANEL_PROP = 80
    MAP_HEIGHT_PROP = 80

    def __init__(self):
        super().__init__()

        self.setMinimumSize(Constants.MIN_WINDOW_SIZE)
        palette = QPalette()
        palette.setColor(QPalette.Active, QPalette.Window, QColor(Constants.Colors.APP_BACKGROUND.value))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self._createWidgets()
        self._configureLayout()

        self._trial = None

    def loadTrialFromMetadata(self, filepath: str):
        if filepath != "":
            with open(filepath, "r") as f:
                self._trial = Trial()
                self._trial.parse(f)
            self._initializeTrial()
            return True

        return False

    def loadTrialFromPackage(self, filepath: str):
        if filepath != "":
            self._trial = Trial()
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
            self._estimatesWidget.updateFor(self._timeSlider.value())

    def closeApp(self):
        self._estimatesWidget.close()

    def _createWidgets(self):
        self._headerPanel = HeaderWidget()

        mapWidth = int(self.width() * TomcatVisualizerWidget.LEFT_PANEL_PROP / 100)
        mapHeight = int(self.height() * TomcatVisualizerWidget.MAP_HEIGHT_PROP / 100)
        self._mapWidget = MapWidget(mapWidth, mapHeight)

        self._timeSlider = TimeSliderWidget(self._onTimeStepChange)
        self._timeSlider.setEnabled(False)

        self._chatHeaderLabel = createLabel("Chat Messages", Constants.Font.SMALL_BOLD.value, Qt.AlignLeft)
        self._chatWidget = ChatWidget()

        self._speechHeaderLabel = createLabel("Speech Transcriptions", Constants.Font.SMALL_BOLD.value, Qt.AlignLeft)
        self._speechWidget = SpeechTranscriptionWidget()

        self._estimatesHeaderLabel = createLabel("Probability Estimates", Constants.Font.SMALL_BOLD.value, "black",
                                                 Qt.AlignLeft)
        self._estimatesWidget = DockEstimates()

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

        speechLayout = QVBoxLayout()
        speechLayout.setContentsMargins(0, 0, 0, 10)
        speechLayout.addWidget(self._speechHeaderLabel)
        speechLayout.addWidget(self._speechWidget)
        speechPanelWidget = QWidget()
        speechPanelWidget.setLayout(speechLayout)

        self._estimatesLayout = QVBoxLayout()
        self._estimatesLayout.setContentsMargins(0, 0, 0, 0)
        self._estimatesLayout.addWidget(self._estimatesHeaderLabel)
        self._estimatesLayout.addWidget(self._estimatesWidget.dockedWidget)
        estimatesPanelWidget = QWidget()
        estimatesPanelWidget.setLayout(self._estimatesLayout)

        rightPanelSplitter = QSplitter(Qt.Vertical)
        rightPanelSplitter.addWidget(chatPanelWidget)
        rightPanelSplitter.addWidget(speechPanelWidget)
        rightPanelSplitter.addWidget(estimatesPanelWidget)

        mainLayout.addLayout(leftPanelLayout, TomcatVisualizerWidget.LEFT_PANEL_PROP)
        mainLayout.addWidget(rightPanelSplitter, 100 - TomcatVisualizerWidget.LEFT_PANEL_PROP)
        mainLayout.setStretch(0, 0)
        mainLayout.setStretch(1, 1)

    def _onTimeStepChange(self, newTimeStep: int):
        self._updateHeaderInfo(newTimeStep)
        self._mapWidget.updateFor(newTimeStep)
        self._chatWidget.updateFor(newTimeStep)
        self._speechWidget.updateFor(newTimeStep)
        self._estimatesWidget.updateFor(newTimeStep)

    def _initializeTrial(self):
        self._mapWidget.reset()
        self._mapWidget.loadMap(self._trial.map)

        self._initializeHeaderInfo()
        self._mapWidget.loadTrial(self._trial)
        self._chatWidget.loadMessages(self._trial.chatMessages[Constants.Player.RED.value],
                                      self._trial.chatMessages[Constants.Player.GREEN.value],
                                      self._trial.chatMessages[Constants.Player.BLUE.value])
        self._speechWidget.loadMessages(self._trial.speechTranscriptions[Constants.Player.RED.value],
                                        self._trial.speechTranscriptions[Constants.Player.GREEN.value],
                                        self._trial.speechTranscriptions[Constants.Player.BLUE.value])

        self._timeSlider.setTimeSteps(self._trial.timeSteps)
        self._timeSlider.reset()
        self._timeSlider.setEnabled(True)

    def _initializeHeaderInfo(self):
        self._headerPanel.setTrialNumber(self._trial.metadata["trial_number"])
        self._headerPanel.setTeamNumber(self._trial.metadata["team_number"])
        self._headerPanel.setRedPlayerName(self._trial.metadata["red_id"])
        self._headerPanel.setGreenPlayerName(self._trial.metadata["green_id"])
        self._headerPanel.setBluePlayerName(self._trial.metadata["blue_id"])
        self._headerPanel.setRedPlayerRole(self._trial.metadata["red_role"])
        self._headerPanel.setGreenPlayerRole(self._trial.metadata["green_role"])
        self._headerPanel.setBluePlayerRole(self._trial.metadata["blue_role"])
        self._updateHeaderInfo(0)

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
