from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import Qt
from block import Block


def draw_block(painter: QPainter, position: Block, block_size: int, color: Qt):
    painter.setPen(QPen(color, 1, Qt.SolidLine))
    painter.setBrush(QBrush(color, Qt.SolidPattern))
    painter.drawRect(position.x * block_size, position.y * block_size, block_size, block_size)
