from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from imap.Gui.Utils import createLabel
from imap.Common.Constants import Constants


class BlackoutWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedWidth(300)
        self.setStyleSheet(f"background-color: red;")

        self._createWidgets()
        self._configureLayout()

    def startAnimation(self):
        self._blackoutLabel.setVisible(True)

    def stopAnimation(self):
        self._blackoutLabel.setVisible(False)

    def _createWidgets(self):
        self._blackoutLabel = createLabel("BLACKOUT", Constants.Font.LARGE_BOLD.value, alignment=Qt.AlignCenter)
        self._blackoutLabel.setVisible(True)

    def _configureLayout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self._blackoutLabel)
