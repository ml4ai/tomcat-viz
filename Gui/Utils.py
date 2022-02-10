from PyQt5.QtWidgets import QLabel
from PyQt5.Qt import QFont, Qt, QPen, QBrush, QGraphicsScene, QGraphicsItem, QLineF


def createLabel(text: str, font: QFont, color: str = "color", alignment: Qt.Alignment = Qt.AlignLeft):
    label = QLabel(text)
    label.setFont(font)
    label.setStyleSheet(f"color: {color}")
    label.setAlignment(alignment)
    return label


def drawBlock(scene: QGraphicsScene, x: float, y: float, scale: int, block_size: int, color: Qt) -> QGraphicsItem:
    pen = QPen(color, 1, Qt.SolidLine)
    brush = QBrush(color, Qt.SolidPattern)
    return scene.addRect(x * scale, y * scale, block_size, block_size, pen, brush)

def drawWall(scene: QGraphicsScene, x: float, y: float, scale: int, block_size: int) -> QGraphicsItem:
    pen = QPen(Qt.lightGray, 1, Qt.SolidLine)
    brush = QBrush(Qt.gray, Qt.SolidPattern)
    return scene.addRect(x * scale, y * scale, block_size, block_size, pen, brush)

def drawCircle(scene: QGraphicsScene, x: float, y: float, scale: int, diameter: int, color: Qt) -> QGraphicsItem:
    pen = QPen(color, 1, Qt.SolidLine)
    brush = QBrush(color, Qt.SolidPattern)
    return scene.addEllipse(x * scale, y * scale, diameter, diameter, pen, brush)


def drawLine(scene: QGraphicsScene, x1: float, y1: float, x2: float, y2: float, scale: int, color: Qt) -> QGraphicsItem:
    pen = QPen(color, 1, Qt.SolidLine)
    line = QLineF(x1 * scale, y1 * scale, x2 * scale, y2 * scale)
    return scene.addLine(line, pen)


