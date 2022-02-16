from PyQt5.Qt import QGraphicsScene, Qt, QPen, QBrush, QFont, QGraphicsItem, QColor

from imap.Gui.StampedRectItem import StampedRectItem
from imap.Parser.MarkerType import MarkerType


class CustomScene(QGraphicsScene):
    def __init__(self, x: int, y: int, width: int, height: int, backgroundColor: Qt):
        super().__init__(x, y, width, height)
        self.setBackgroundBrush(backgroundColor)

    def drawWall(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.gray, Qt.lightGray)

    def drawRed(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawCircle(x, y, scale, blockSize, QColor("#E30B21"), QColor("#E30B21"))

    def drawGreen(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawCircle(x, y, scale, blockSize, QColor("#13F000"), QColor("#13F000"))

    def drawBlue(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawCircle(x, y, scale, blockSize, QColor("#0045FA"), QColor("#0045FA"))

    def drawVictimSignalBlock(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawStampedBlock("V", x, y, scale, blockSize, Qt.white, Qt.black, Qt.black)

    def drawGravel(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.darkGray, Qt.darkGray, Qt.Dense5Pattern)

    def drawVictimA(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawStampedBlock("A", x, y, scale, blockSize, QColor("#02B860"), QColor("#02B860"), Qt.black)

    def drawVictimB(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawStampedBlock("B", x, y, scale, blockSize, QColor("#02B860"), QColor("#02B860"), Qt.black)

    def drawCriticalVictim(self, x: float, y: float, scale: float, blockSize: float):
        # return self._drawBlock(x, y, scale, blockSize, QColor("#FACC09"), QColor("#FACC09"))
        return self._drawStampedBlock("C", x, y, scale, blockSize, QColor("#FACC09"), QColor("#FACC09"), Qt.black)

    def drawSafeVictimA(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawStampedBlock("A", x, y, scale, blockSize, QColor("#0AB7FC"), QColor("#0AB7FC"), Qt.black)

    def drawRubbleCollapseBlock(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, QColor("#8400EB"), QColor("#8400EB"))

    def drawDoor(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.black, Qt.white, Qt.Dense7Pattern)

    def drawEmptyBlock(self, x: float, y: float, scale: float, blockSize: float):
        return self._drawBlock(x, y, scale, blockSize, Qt.white, Qt.white)

    def drawMarker(self, type: MarkerType, x: float, y: float, scale: float, blockSize: float):
        label = "X"
        if type == MarkerType.NO_VICTIM:
            label = "O"
        elif type == MarkerType.VICTIM_A:
            label = "A"
        elif type == MarkerType.VICTIM_B:
            label = "B"
        elif type == MarkerType.REGULAR_VICTIM:
            label = "R"
        elif type == MarkerType.CRITICAL_VICTIM:
            label = "C"
        elif type == MarkerType.THREAT_ROOM:
            label = "T"
        elif type == MarkerType.SOS:
            label = "S"

        return self._drawStampedBlock(label, x, y, scale, blockSize, QColor("#E602D5"), QColor("#E602D5"), Qt.black)

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
