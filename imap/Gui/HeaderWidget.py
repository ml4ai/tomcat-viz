from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLayout
from PyQt5.Qt import Qt

from imap.Gui.PlayerPanelWidget import PlayerPanelWidget
from imap.Gui.LegendWidget import LegendWidget
from imap.Gui.BlackoutWidget import BlackoutWidget
from imap.Gui.Utils import createLabel, createVerticalSeparator
from imap.Common.Constants import Constants


class HeaderWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._createWidgets()
        self._configureLayout()

    def _createWidgets(self):
        # Legend
        self._legendPanel = LegendWidget()

        # Central info
        self._trialLabel = createLabel("T00000", Constants.Font.SMALL_REGULAR.value, "gray")
        self._teamLabel = createLabel("TM00000", Constants.Font.SMALL_REGULAR.value, "gray")
        self._scoreLabel = createLabel("0", Constants.Font.HUGE_BOLD.value, alignment=Qt.AlignCenter)

        # Player panels
        self._redPanel = PlayerPanelWidget(Constants.Colors.RED_PLAYER.value)
        self._redPanel.setEquippedItem(Constants.EquippedItem.MEDICAL_KIT)
        self._greenPanel = PlayerPanelWidget(Constants.Colors.GREEN_PLAYER.value)
        self._greenPanel.setEquippedItem(Constants.EquippedItem.STRETCHER)
        self._bluePanel = PlayerPanelWidget(Constants.Colors.BLUE_PLAYER.value)
        self._bluePanel.setEquippedItem(Constants.EquippedItem.HAMMER)

        # Blackout area
        self._blackoutPanel = BlackoutWidget()

    def setRedPlayerName(self, name: str):
        self._redPanel.setName(name)

    def setGreenPlayerName(self, name: str):
        self._greenPanel.setName(name)

    def setBluePlayerName(self, name: str):
        self._bluePanel.setName(name)

    def setRedPlayerRole(self, role: Constants.Role):
        self._redPanel.setRole(role)

    def setGreenPlayerRole(self, role: Constants.Role):
        self._greenPanel.setRole(role)

    def setBluePlayerRole(self, role: Constants.Role):
        self._bluePanel.setRole(role)

    def setRedPlayerAction(self, action: Constants.Action):
        self._redPanel.setAction(action)

    def setGreenPlayerAction(self, action: Constants.Action):
        self._greenPanel.setAction(action)

    def setBluePlayerAction(self, action: Constants.Action):
        self._bluePanel.setAction(action)

    def setRedPlayerEquippedItem(self, item: Constants.EquippedItem):
        self._redPanel.setEquippedItem(item)

    def setGreenPlayerEquippedItem(self, item: Constants.EquippedItem):
        self._greenPanel.setEquippedItem(item)

    def setBluePlayerEquippedItem(self, item: Constants.EquippedItem):
        self._bluePanel.setEquippedItem(item)

    def setScore(self, score: int):
        self._scoreLabel.setText(f"{score}")

    def setTrialNumber(self, trialNumber: str):
        self._trialLabel.setText(trialNumber)
        self._trialLabel.adjustSize()

    def setTeamNumber(self, teamNumber: str):
        self._teamLabel.setText(teamNumber)
        self._teamLabel.adjustSize()

    def showBlackout(self):
        self._blackoutPanel.startAnimation()

    def hideBlackout(self):
        self._blackoutPanel.stopAnimation()

    def _configureLayout(self):
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        centralLayout = self._getCentralLayout()
        mainLayout.addWidget(self._legendPanel, 19)
        mainLayout.addWidget(createVerticalSeparator(), 1)
        mainLayout.addLayout(centralLayout, 60)
        mainLayout.addWidget(createVerticalSeparator(), 1)
        mainLayout.addWidget(self._blackoutPanel, 19)
        mainLayout.addStretch()

    def _getCentralLayout(self) -> QLayout:
        trialNumberFormLayout = QFormLayout()
        trialNumberFormLayout.addRow(createLabel("Trial:", Constants.Font.SMALL_BOLD.value), self._trialLabel)
        trialNumberFormLayout.setFormAlignment(Qt.AlignRight)
        trialNumberFormLayout.setLabelAlignment(Qt.AlignLeft)
        trialNumberFormLayout.setContentsMargins(0, 0, 10, 0)
        teamNumberFormLayout = QFormLayout()
        teamNumberFormLayout.addRow(createLabel("Team:", Constants.Font.SMALL_BOLD.value), self._teamLabel)
        teamNumberFormLayout.setFormAlignment(Qt.AlignLeft)
        teamNumberFormLayout.setLabelAlignment(Qt.AlignLeft)
        teamNumberFormLayout.setContentsMargins(10, 0, 0, 0)

        trialInfoLayout = QHBoxLayout()
        trialInfoLayout.addLayout(trialNumberFormLayout, 40)
        trialInfoLayout.addWidget(createLabel("<html><head/><body><p>&#9670;</p></body></html>",
                                              Constants.Font.SMALL_REGULAR.value, "black", Qt.AlignHCenter))
        trialInfoLayout.addLayout(teamNumberFormLayout, 40)

        playerInfoLayout = QHBoxLayout()
        playerInfoLayout.setContentsMargins(0, 0, 0, 0)
        playerInfoLayout.addWidget(self._redPanel)
        playerInfoLayout.addWidget(createVerticalSeparator())
        playerInfoLayout.addWidget(self._greenPanel)
        playerInfoLayout.addWidget(createVerticalSeparator())
        playerInfoLayout.addWidget(self._bluePanel)

        layout = QVBoxLayout()
        layout.addLayout(trialInfoLayout, 10)
        layout.addWidget(self._scoreLabel, 60)
        layout.addLayout(playerInfoLayout, 40)

        return layout
