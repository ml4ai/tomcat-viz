from PyQt5.Qt import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem


class StampedRectItem(QGraphicsItem):

    def __init__(self, rectItem: QGraphicsRectItem, textItem: QGraphicsTextItem):
        super().__init__()
        self.rectItem = rectItem
        self.textItem = textItem
