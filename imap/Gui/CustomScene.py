from PyQt5.Qt import QGraphicsScene, Qt, QPen, QBrush, QFont, QGraphicsItem
from imap.Gui.StampedRectItem import StampedRectItem


class CustomScene(QGraphicsScene):
    def __init__(self, x: int, y: int, width: int, height: int, backgroundColor: Qt):
        super().__init__(x, y, width, height)
        self.setBackgroundBrush(backgroundColor)

    def drawWall(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.gray, Qt.lightGray)

    def drawRed(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawCircle(x, y, scale, blockSize, Qt.red, Qt.red)

    def drawGreen(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawCircle(x, y, scale, blockSize, Qt.green, Qt.green)

    def drawBlue(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawCircle(x, y, scale, blockSize, Qt.blue, Qt.blue)

    def drawVictimSignalBlock(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawStampedBlock("V", x, y, scale, blockSize, Qt.white, Qt.black, Qt.black)

    def drawGravel(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.darkGray, Qt.darkGray, Qt.Dense5Pattern)

    def drawVictimA(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawStampedBlock("A", x, y, scale, blockSize, Qt.darkGreen, Qt.darkGreen, Qt.white)

    def drawVictimB(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawStampedBlock("B", x, y, scale, blockSize, Qt.darkGreen, Qt.darkGreen, Qt.white)

    def drawCriticalVictim(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.darkYellow, Qt.darkYellow)

    def drawRubbleCollapseBlock(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.red, Qt.red)

    def drawDoor(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.black, Qt.white, Qt.Dense7Pattern)

    def drawEmptyBlock(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.white, Qt.white)

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
        rectItem = self.addRect(x * scale, y * scale, blockSize, blockSize, pen, brush)

        textItem = self.addText(text, QFont('Arial', 110 / blockSize))
        textItem.setDefaultTextColor(textColor)
        textItem.setPos((x - 2 / blockSize) * scale, (y - 5.5 / blockSize) * scale)
        return StampedRectItem(rectItem, textItem)

    def _drawBlock(self, x: float, y: float, scale: float, block_size: float, color: Qt,
                   borderColor: Qt, brushPattern: Qt = Qt.SolidPattern) -> QGraphicsItem:
        pen = QPen(borderColor, 1, Qt.SolidLine)
        brush = QBrush(color, brushPattern)
        return self.addRect(x * scale, y * scale, block_size, block_size, pen, brush)

    def _drawCircle(self, x: float, y: float, scale: float, diameter: float, color: Qt,
                    borderColor: Qt) -> QGraphicsItem:
        pen = QPen(borderColor, 1, Qt.SolidLine)
        brush = QBrush(color, Qt.SolidPattern)
        return self.addEllipse(x * scale, y * scale, diameter, diameter, pen, brush)
