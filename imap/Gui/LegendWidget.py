from PyQt5.QtWidgets import QWidget, QVBoxLayout

from imap.Gui.Utils import createLabel
from imap.Common.Constants import Constants


class LegendWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._createWidgets()
        self._configureLayout()

    def _createWidgets(self):
        self._redSquareLabel = createLabel("Red Player", Constants.Font.TINY_REGULAR.value)
        self._greenSquareLabel = createLabel("Green Player", Constants.Font.TINY_REGULAR.value)
        self._blueSquareLabel = createLabel("Blue Player", Constants.Font.TINY_REGULAR.value)

    def _configureLayout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self._redSquareLabel)
        layout.addWidget(self._greenSquareLabel)
        layout.addWidget(self._blueSquareLabel)
        layout.addStretch()
