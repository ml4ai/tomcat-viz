import os

import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.Qt import QFont, Qt, QPainter

from Gui.Utils import createLabel, drawBlock
from PreProcessing.MapParser import MapParser

class MapWidget(QWidget):

    def __init__(self, gridFilepath: str = None, showGrid: bool = False, blockSize: int = 10):
        super().__init__()
        self.gridFilepath = gridFilepath
        self._showGrid = showGrid
        self._blockSize = blockSize
        self._painter = QPainter()

    def paintEvent(self, event):
        self._painter.begin(self)
        self._drawStaticBlocks()
        # if self._show_grid:
        #     draw_grid(self._map_bounds.x1 * self._block_size, self._map_bounds.y1 * self._block_size,
        #               self._map_bounds.x2 * self._block_size, self._map_bounds.y2 * self._block_size,
        #               self._block_size)
        self._painter.end()

    # def minimumSizeHint(self):
    #     return QSize(self._block_size * self._map_bounds.width() + self.margin,
    #                  self._block_size * (self._map_bounds.height() + 2) + self.margin)

    def _drawStaticBlocks(self):
        if self.gridFilepath is None or not os.path.exists(self.gridFilepath):
            return

        grid = np.loadtxt(self.gridFilepath, dtype=np.int8)

        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                if grid[i][j] == MapParser.WALL:
                    drawBlock(self._painter, j, i, self._blockSize, Qt.gray)
                elif grid[i][j] == MapParser.DOOR:
                    drawBlock(self._painter, j, i, self._blockSize, Qt.red)


        # self.setStyleSheet("background-color: green")
        # layout = QHBoxLayout()
        # layout.addWidget(createLabel("Map", QFont("Arial", 40), "white", Qt.AlignCenter))
        # layout.setContentsMargins(0, 0, 0, 0)
        # self.setLayout(layout)