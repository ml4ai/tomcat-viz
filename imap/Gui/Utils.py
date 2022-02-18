from PyQt5.QtWidgets import QLabel, QFrame, QWidget, QVBoxLayout
from PyQt5.Qt import QFont, Qt, QSize


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


def createEmptyWidget(backgroundColor: str, size: QSize = None):
    widget = QWidget()
    widget.setStyleSheet(f"background-color:{backgroundColor};")
    if size is not None:
        widget.setFixedSize(size)
    return widget


def createStampedBlockWidget(text: str, font: QFont, textColor: str, backgroundColor: str, widgetSize: QSize = None):
    widget = QWidget()
    widget.setStyleSheet(f"background-color:{backgroundColor};")
    if widgetSize is not None:
        widget.setFixedSize(widgetSize)
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    centralLabel = createLabel(text, font, textColor, Qt.AlignCenter)
    layout.addWidget(centralLabel)
    return widget


def createPatternWidget(backgroundColor: str, size: QSize = None, pattern: Qt = Qt.SolidPattern):
    if pattern == Qt.SolidPattern:
        return createEmptyWidget(backgroundColor, size)
    else:
        widget = QWidget()
        widget.setStyleSheet(f"background-color:{backgroundColor};")
        if size is not None:
            widget.setFixedSize(size)
        return widget
