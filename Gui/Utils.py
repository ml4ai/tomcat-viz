from PyQt5.QtWidgets import QLabel
from PyQt5.Qt import QFont, Qt, QPen, QBrush, QPainter


def createLabel(text: str, font: QFont, color: str = "color", alignment: Qt.Alignment = Qt.AlignLeft):
    label = QLabel(text)
    label.setFont(font)
    label.setStyleSheet(f"color: {color}")
    label.setAlignment(alignment)
    return label


def drawBlock(painter: QPainter, x: int, y: int, block_size: int, color: Qt):
    painter.setPen(QPen(color, 1, Qt.SolidLine))
    painter.setBrush(QBrush(color, Qt.SolidPattern))
    painter.drawRect(x * block_size, y * block_size, block_size, block_size)
