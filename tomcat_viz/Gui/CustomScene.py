from PyQt5.Qt import QGraphicsScene, Qt, QPen, QBrush, QFont, QGraphicsItem, QColor, QGraphicsEllipseItem

from tomcat_viz.Gui.StampedRectItem import StampedRectItem
from tomcat_viz.Common.Constants import Constants


class CustomScene(QGraphicsScene):
    def __init__(self, x: int, y: int, width: int, height: int, backgroundColor: Qt):
        super().__init__(x, y, width, height)
        self.setBackgroundBrush(backgroundColor)

    def drawWall(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        return self._drawBlock(x, y, scale, blockSize, Qt.gray, Qt.lightGray)

    def drawRed(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.RED_PLAYER.value)
        return self._drawCircle(x, y, scale, blockSize, color, color)

    def drawGreen(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.GREEN_PLAYER.value)
        return self._drawCircle(x, y, scale, blockSize, color, color)

    def drawBlue(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.BLUE_PLAYER.value)
        return self._drawCircle(x, y, scale, blockSize, color, color)

    def drawVictimSignalBlock(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        return self._drawStampedBlock("V", x, y, scale, blockSize, Qt.white, Qt.black, Qt.black)

    def drawRubble(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.RUBBLE.value)
        return self._drawBlock(x, y, scale, blockSize, color, color, Qt.Dense5Pattern)

    def drawVictimA(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.VICTIM_A.value)
        return self._drawStampedBlock("A", x, y, scale, blockSize, color, color, Qt.black)

    def drawVictimB(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.VICTIM_B.value)
        return self._drawStampedBlock("B", x, y, scale, blockSize, color, color, Qt.black)

    def drawCriticalVictim(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.CRITICAL_VICTIM.value)
        return self._drawStampedBlock("C", x, y, scale, blockSize, color, color, Qt.black)

    def drawSafeVictimA(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.SAFE_VICTIM.value)
        return self._drawStampedBlock("A", x, y, scale, blockSize, color, color, Qt.black)

    def drawSafeVictimB(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.SAFE_VICTIM.value)
        return self._drawStampedBlock("B", x, y, scale, blockSize, color, color, Qt.black)

    def drawSafeCriticalVictim(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.SAFE_VICTIM.value)
        return self._drawStampedBlock("C", x, y, scale, blockSize, color, color, Qt.black)

    def drawRubbleCollapseBlock(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.THREAT_ACTIVATION.value)
        return self._drawBlock(x, y, scale, blockSize, color, color)

    def drawDoor(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.DOOR.value)
        return self._drawBlock(x, y, scale, blockSize, color, Qt.white, Qt.Dense7Pattern)

    def drawMissingVictim(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.INCONSISTENCY.value)
        return self._drawStampedBlock("X", x, y, scale, blockSize, color, color, Qt.black)

    def drawEmptyBlock(self, x: float, y: float, scale: float, blockSize: float) -> QGraphicsItem:
        return self._drawBlock(x, y, scale, blockSize, Qt.white, Qt.white)

    def drawMarker(self, markerType: Constants.MarkerType, x: float, y: float, scale: float,
                   blockSize: float) -> QGraphicsItem:
        label = Constants.MARKER_TYPE_MAP.get(markerType, "X")

        color = QColor(Constants.Colors.MARKER.value)
        return self._drawStampedBlock(label, x, y, scale, blockSize, color, color, Qt.black)

    def drawRedHeading(self, x: float, y: float, yaw: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.RED_PLAYER.value)
        return self._drawPlayerHeading(x, y, yaw, scale, blockSize, color)

    def drawGreenHeading(self, x: float, y: float, yaw: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.GREEN_PLAYER.value)
        return self._drawPlayerHeading(x, y, yaw, scale, blockSize, color)

    def drawBlueHeading(self, x: float, y: float, yaw: float, scale: float, blockSize: float) -> QGraphicsItem:
        color = QColor(Constants.Colors.BLUE_PLAYER.value)
        return self._drawPlayerHeading(x, y, yaw, scale, blockSize, color)

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
                          borderColor: Qt, textColor: Qt) -> StampedRectItem:
        pen = QPen(borderColor, 1, Qt.SolidLine)
        brush = QBrush(color, Qt.SolidPattern)
        rectItem = self.addRect(x * scale + 1, y * scale + 1, blockSize - 1, blockSize - 1, pen, brush)

        textItem = self.addText(text, QFont('Arial', int(100 / blockSize)))
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

    def _drawPlayerHeading(self, x: float, y: float, yaw: float, scale: float, blockSize: float,
                           color: QColor) -> QGraphicsItem:
        pen = QPen(color, 1, Qt.SolidLine)
        brush = QBrush(color, Qt.SolidPattern)
        radius = (5 * blockSize) / 2
        item = QGraphicsEllipseItem((x + 0.5) * scale - radius, (y + 0.5) * scale - radius, 2 * radius, 2 * radius)
        span = 45
        start_angle = (270 - yaw - (span / 2)) % 360
        item.setStartAngle(start_angle * 16)
        item.setSpanAngle(span * 16)
        item.setPen(pen)
        item.setBrush(brush)
        item.setOpacity(0.5)
        self.addItem(item)

        return item
