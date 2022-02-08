from PyQt5.QtGui import QPainter, QPen, QFont, QFontMetrics
from PyQt5.QtCore import Qt


def draw_grid(painter: QPainter, min_x: int, min_y: int, max_x: int, max_y: int, stride: int, color: Qt = Qt.black):
    pen = QPen(color, 1, Qt.DashLine)
    painter.setPen(pen)
    font = QFont()
    font.setPointSize(10)
    painter.setFont(font)
    fm = QFontMetrics(font)
    font_height_in_pixels = fm.height()
    offset = (stride - font_height_in_pixels) / 2 + font_height_in_pixels

    # Horizontal lines
    for y in range(min_y, max_y + 1, stride):
        painter.drawLine(min_x, y, max_x, y)
        if y < max_y:
            painter.drawText(min_x - 40, y + offset, f"{int(y / stride)}")

    # Vertical lines
    for x in range(min_x, max_x + 1, stride):
        painter.drawLine(x, min_y, x, max_y)
        if x < max_x:
            painter.save()
            painter.translate(x + offset, min_y - 10)
            painter.rotate(-90)
            painter.drawText(0, 0, f"{int(x / stride)}")
            painter.restore()
