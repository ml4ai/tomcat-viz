from PyQt5.Qt import QFont, Qt, QSize, QPalette, QColor, QBrush, QPainter, QPen
from PyQt5.QtWidgets import QLabel, QFrame, QWidget


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


class BlockIconWidget(QWidget):

    def __init__(self, backgroundColor: str, borderColor: str, size: QSize = None, pattern: Qt = None,
                 patternColor: str = None, text: str = None, textColor: str = None, font: QFont = None):
        super().__init__()

        self._borderPen = QPen(QColor(borderColor), 1, Qt.SolidLine)
        self._brush = None if patternColor is None or pattern is None else QBrush(QColor(patternColor), pattern)
        self._text = text
        self._textPen = None if textColor is None else QPen(QColor(textColor), 1, Qt.SolidLine)
        self._font = font
        palette = QPalette()
        palette.setColor(QPalette.Active, QPalette.Window, QColor(backgroundColor))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.setFixedSize(size)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(self._borderPen)
        if self._brush is not None:
            painter.setBrush(self._brush)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        if self._text is not None:
            painter.setPen(self._textPen)
            if self._font is not None:
                painter.setFont(self._font)
            painter.drawText(event.rect(), Qt.AlignCenter, self._text)
        painter.end()


def createStampedBlockWidget(text: str, font: QFont, textColor: str, backgroundColor: str, widgetSize: QSize = None):
    # Simpler version of a BlockIcon with no pattern and border with the same color as the background
    return BlockIconWidget(backgroundColor, backgroundColor, widgetSize, Qt.SolidPattern, backgroundColor, text,
                           textColor, font)



