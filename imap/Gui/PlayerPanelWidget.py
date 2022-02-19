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
        boldFont = QFont("Arial", 14, QFont.Bold)
        regularFont = QFont("Arial", 14)

        self._nameLabel = createLabel("NAME", boldFont, color, Qt.AlignCenter)
        self._equippedItemIcon = EquippedItemWidget(20, 20)
        self._actionLabel = createLabel("Player is doing...", regularFont, "gray", Qt.AlignCenter)

    def _configureLayout(self):
        main_layout = QVBoxLayout(self)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self._equippedItemIcon)
        bottom_layout.addWidget(createVerticalSeparator())
        bottom_layout.addWidget(self._actionLabel)
        bottom_layout.addStretch()

        main_layout.addWidget(self._nameLabel)
        main_layout.addLayout(bottom_layout)

