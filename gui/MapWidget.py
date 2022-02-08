from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.Qt import QFont, Qt

from utils import gui


class MapWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: green")
        layout = QHBoxLayout()
        layout.addWidget(gui.createLabel("Map", QFont("Arial", 40), "white", Qt.AlignCenter))
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)