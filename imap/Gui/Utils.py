from PyQt5.QtWidgets import QLabel, QFrame
from PyQt5.Qt import QFont, Qt


def createLabel(text: str, font: QFont, color: str = "color", alignment: Qt.Alignment = Qt.AlignLeft) -> QLabel:
    label = QLabel(text)
    label.setFont(font)
    label.setStyleSheet(f"color: {color}")
    label.setAlignment(alignment)
    label.adjustSize()
    return label


def createVerticalSeparator() -> QFrame:
    separator = QFrame()
    separator.setFrameShape(QFrame.VLine)
    separator.setFrameShadow(QFrame.Sunken)
    return separator


def createHorizontalSeparator() -> QFrame:
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    return separator



