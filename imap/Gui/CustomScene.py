from PyQt5.Qt import QGraphicsScene, Qt, QPen, QBrush, QFont, QGraphicsItem, QColor

from imap.Gui.StampedRectItem import StampedRectItem
from imap.Common.Constants import Constants


class CustomScene(QGraphicsScene):
    def __init__(self, x: int, y: int, width: int, height: int, backgroundColor: Qt):
        super().__init__(x, y, width, height)
        self.setBackgroundBrush(backgroundColor)

    def drawWall(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.gray, Qt.lightGray)

    def drawRed(self, x: float, y: float, scale: float, blockSize: float):
        color = QColor(Constants.Colors.RED_PLAYER.value)
        return self._drawCircle(x, y, scale, blockSize, color, color)

    def drawGreen(self, x: float, y: float, scale: float, blockSize: float):
        color = QColor(Constants.Colors.GREEN_PLAYER.value)
        return self._drawCircle(x, y, scale, blockSize, color, color)

    def drawBlue(self, x: float, y: float, scale: float, blockSize: float):
        color = QColor(Constants.Colors.BLUE_PLAYER.value)
        return self._drawCircle(x, y, scale, blockSize, color, color)

    def drawVictimSignalBlock(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawStampedBlock("V", x, y, scale, blockSize, Qt.white, Qt.black, Qt.black)

    def drawGravel(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.darkGray, Qt.darkGray, Qt.Dense5Pattern)

    def drawVictimA(self, x: float, y: float, scale: float, blockSize: float):
        color = QColor(Constants.Colors.VICTIM_A.value)
        return self._drawStampedBlock("A", x, y, scale, blockSize, color, color, Qt.black)

    def drawVictimB(self, x: float, y: float, scale: float, blockSize: float):
        color = QColor(Constants.Colors.VICTIM_B.value)
        return self._drawStampedBlock("B", x, y, scale, blockSize, color, color, Qt.black)

    def drawCriticalVictim(self, x: float, y: float, scale: float, blockSize: float):
        color = QColor(Constants.Colors.CRITICAL_VICTIM.value)
        return self._drawStampedBlock("C", x, y, scale, blockSize, color, color, Qt.black)

    def drawSafeVictimA(self, x: float, y: float, scale: float, blockSize: float):
        color = QColor(Constants.Colors.SAFE_VICTIM.value)
        return self._drawStampedBlock("A", x, y, scale, blockSize, color, color, Qt.black)

    def drawRubbleCollapseBlock(self, x: float, y: float, scale: float, blockSize: float):
        color = QColor(Constants.Colors.THREAT_ACTIVATION.value)
        return self._drawBlock(x, y, scale, blockSize, color, color)

    def drawDoor(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.black, Qt.white, Qt.Dense7Pattern)

    def drawEmptyBlock(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.white, Qt.white)

    def drawMarker(self, type: Constants.MarkerType, x: float, y: float, scale: float, blockSize: float):
        label = "X"
        if type == Constants.MarkerType.NO_VICTIM:
            label = "O"
        elif type == Constants.MarkerType.VICTIM_A:
            label = "A"
        elif type == Constants.MarkerType.VICTIM_B:
            label = "B"
        elif type == Constants.MarkerType.REGULAR_VICTIM:
            label = "R"
        elif type == Constants.MarkerType.CRITICAL_VICTIM:
            label = "C"
        elif type == Constants.MarkerType.THREAT_ROOM:
            label = "T"
        elif type == Constants.MarkerType.SOS:
            label = "S"

        color = QColor(Constants.Colors.MARKER.value)
        return self._drawStampedBlock(label, x, y, scale, blockSize, color, color, Qt.black)

    def addItem(self, item: QGraphicsItem) -> None:
        if isinstance(item, StampedRectItem):
            super().addItem(item.rectItem)
            super().addItem(item.textItem)
        else:
            super().addItem(item)

    def removeItem(self, item: QGraphicsItem) -> None:
        if isinstance(item, StampedRectItem):
            super().removeItem(item.rectItem)
            super().removeItem(item.textItem)
        else:
            super().removeItem(item)

    def _drawStampedBlock(self, text: str, x: float, y: float, scale: float, blockSize: float, color: Qt,
                          borderColor: Qt, textColor: Qt):
        pen = QPen(borderColor, 1, Qt.SolidLine)
        brush = QBrush(color, Qt.SolidPattern)
        rectItem = self.addRect(x * scale + 1, y * scale + 1, blockSize - 1, blockSize - 1, pen, brush)

        textItem = self.addText(text, QFont('Arial', 100 / blockSize))
        textItem.setDefaultTextColor(textColor)
        textItem.setPos((x - 2 / blockSize) * scale, (y - 4.5 / blockSize) * scale)
        return StampedRectItem(rectItem, textItem)

    def _drawBlock(self, x: float, y: float, scale: float, block_size: float, color: Qt,
                   borderColor: Qt, brushPattern: Qt = Qt.SolidPattern) -> QGraphicsItem:
        pen = QPen(borderColor, 1, Qt.SolidLine)
        brush = QBrush(color, brushPattern)
        return self.addRect(x * scale + 1, y * scale + 1, block_size - 1, block_size - 1, pen, brush)

    def _drawCircle(self, x: float, y: float, scale: float, diameter: float, color: Qt,
                    borderColor: Qt) -> QGraphicsItem:
        pen = QPen(borderColor, 1, Qt.SolidLine)
        brush = QBrush(color, Qt.SolidPattern)
        return self.addEllipse(x * scale, y * scale, diameter, diameter, pen, brush)
