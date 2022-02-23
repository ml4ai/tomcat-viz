from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.Qt import QFont, QPixmap
from PyQt5.QtCore import Qt, QSize

from imap.Gui.Utils import createLabel, createVerticalSeparator, createEmptyWidget
from imap.Common.Constants import Constants
from imap.Gui.EquippedItemWidget import EquippedItemWidget


class PlayerPanelWidget(QWidget):

    def __init__(self, color: str):
        super().__init__()
        self._createWidgets(color)
        self._configureLayout()

    def setName(self, name: str):
        self._nameLabel.setText(name)

    def setRole(self, role: Constants.Role):
        label = "UNKNOWN"
        if role == Constants.Role.MEDIC:
            label = "Medic"
        elif role == Constants.Role.ENGINEER:
            label = "Engineer"
        elif role == Constants.Role.TRANSPORTER:
            label = "Transporter"

        self._roleLabel.setText(label)

    def setEquippedItem(self, item: Constants.EquippedItem):
        self._equippedItemIcon.setItem(item)

    def setAction(self, action: Constants.Action):
        text = ""
        if action == Constants.Action.HEALING_VICTIM:
            text = "Healing victim..."
        elif action == Constants.Action.CARRYING_VICTIM:
            text = "Carrying victim..."
        elif action == Constants.Action.DESTROYING_RUBBLE:
            text = "Destroying rubble..."

        self._actionLabel.setText(text)

    def _createWidgets(self, color: str):
        self._nameLabel = createLabel("NAME", Constants.Font.SMALL_BOLD.value, color, Qt.AlignRight)
        self._nameRoleSep = createLabel("<html><head/><body><p>&#9670;</p></body></html>",
                                        Constants.Font.SMALL_REGULAR.value, color, Qt.AlignHCenter)
        self._roleLabel = createLabel("ROLE", Constants.Font.SMALL_BOLD.value, color, Qt.AlignLeft)
        self._equippedItemIcon = EquippedItemWidget(20, 20)
        self._actionLabel = createLabel("Player is doing...", Constants.Font.SMALL_REGULAR.value, "gray",
                                        Qt.AlignCenter)

    def _configureLayout(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(10, 0, 0, 10)

        upperLayout = QHBoxLayout()
        upperLayout.setContentsMargins(0, 0, 0, 0)
        upperLayout.addWidget(self._nameLabel)
        upperLayout.addWidget(self._nameRoleSep)
        upperLayout.addWidget(self._roleLabel)

        bottomLayout = QHBoxLayout()
        bottomLayout.setContentsMargins(0, 0, 0, 0)
        bottomLayout.addWidget(self._equippedItemIcon)
        bottomLayout.addWidget(createVerticalSeparator())
        bottomLayout.addWidget(self._actionLabel)
        bottomLayout.addStretch()

        mainLayout.addLayout(upperLayout)
        mainLayout.addLayout(bottomLayout)
        mainLayout.addStretch()
