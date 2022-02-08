from typing import Any

from PyQt5.QtWidgets import QLabel
from PyQt5.Qt import QFont, Qt


def createLabel(text: str, font: QFont, color: str = "color", alignment: Qt.Alignment = Qt.AlignLeft):
    label = QLabel(text)
    label.setFont(font)
    label.setStyleSheet(f"color: {color}")
    label.setAlignment(alignment)
    return label
