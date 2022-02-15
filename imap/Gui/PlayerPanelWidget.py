from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.Qt import QFont
from PyQt5.QtCore import Qt

from imap.Gui.Utils import createLabel, createVerticalSeparator
from imap.Common.Constants import Constants


class PlayerPanelWidget(QWidget):

    def __init__(self, color: str):
        super().__init__()
        self._createWidgets(color)
        self._configureLayout()

    def setName(self, name: str):
        self._nameLabel.setText(name)

    def setEquippedItem(self, item: str):
        pass

    def setAction(self, action: str):
        text = ""
        if action == Constants.Action.HEALING_VICTIM.value:
            text = "Healing victim..."
        elif action == Constants.Action.CARRYING_VICTIM.value:
            text = "Carrying victim..."
        elif action == Constants.Action.DESTROYING_RUBBLE.value:
            text = "Destroying rubble..."

        self._actionLabel.setText(text)

    def _createWidgets(self, color: str):
        boldFont = QFont("Arial", 14, QFont.Bold)
        regularFont = QFont("Arial", 14)

        self._nameLabel = createLabel("", boldFont, color, Qt.AlignCenter)
        self._equippedItemIcon = self.createWidget(color)
        self._actionLabel = createLabel("", regularFont, "gray", Qt.AlignLeft)

    def _configureLayout(self):
        main_layout = QVBoxLayout(self)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self._equippedItemIcon)
        bottom_layout.addWidget(createVerticalSeparator())
        bottom_layout.addWidget(self._actionLabel)
        bottom_layout.addStretch()

        main_layout.addWidget(self._nameLabel)
        main_layout.addLayout(bottom_layout)

    def createWidget(self, color: str):
        # To be removed
        widget = QWidget()
        widget.setStyleSheet(f"background-color:{color};")
        widget.setFixedSize(20, 20)
        return widget

