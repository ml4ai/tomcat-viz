import os
from enum import Enum
from typing import List, Tuple

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.Qt import QFont, Qt, QPainter, QImage, QSize, QGraphicsView, QGraphicsScene, QGraphicsItem, QPainterPath, \
    QLineF, QPen
import numpy as np
import json
import pickle
import copy

from Gui.Utils import drawBlock, drawCircle, drawLine, drawWall
from PreProcessing.MapParser import MapParser


class MapWidget(QWidget):
    class DrawingDirection(Enum):
        NEXT = 0
        PREVIOUS = 1

    def __init__(self, width: int, height: int, showGrid: bool = False, blockSize: int = 10, playerSize: int = 8):
        super().__init__()
        self._showGrid = showGrid
        self._blockSize = blockSize
        self._playerSize = playerSize

        self._scene = QGraphicsScene(0, 0, width, height)
        self._scene.setBackgroundBrush(Qt.white)
        self._view = QGraphicsView(self._scene, self)

        self._mapMetadata = None

        self._missionMetadata = None
        self._playersPositions = None
        self._scores = None
        self._lastDrawnTimeStep = -1

        # Stores objects draw per time step
        self._currPlayersBlocks = []
        # self._trajectories = []
        self._playersPaths = []
        self._playersPathItems = []

    def loadMap(self, mapDir: str):
        with open(os.path.join(mapDir, "metadata.json"), "r") as f:
            self._mapMetadata = json.load(f)

        gridMap = np.loadtxt(os.path.join(mapDir, "grid_map.txt"), dtype=np.int16)
        self._drawWallsAndDoors(gridMap)

    def loadMission(self, missionDir: str):
        if os.path.exists(missionDir):
            with open(os.path.join(missionDir, "metadata.json"), "r") as f:
                self._missionMetadata = json.load(f)

            self._playersPositions = [
                np.loadtxt(os.path.join(missionDir, "positions_red.txt")),
                np.loadtxt(os.path.join(missionDir, "positions_green.txt")),
                np.loadtxt(os.path.join(missionDir, "positions_blue.txt")),
            ]

            self._drawInitialVictimsAndRubbles()
            self._placePlayersInTheMap()
            self._lastDrawnTimeStep = 0

    def updateFor(self, timeStep: int):
        if timeStep > self._lastDrawnTimeStep:
            for t in range(self._lastDrawnTimeStep + 1, timeStep + 1):
                self._erasePlayersBlocks()
                previous_positions = self._getPlayersPositionsAt(t - 1)
                positions = self._getPlayersPositionsAt(t)
                self._drawTrajectories(previous_positions, positions)
                self._drawPlayers(positions)
        else:
            for t in range(self._lastDrawnTimeStep - 1, timeStep - 1, -1):
                self._erasePlayersBlocks()
                self._popTrajectories()
                positions = self._getPlayersPositionsAt(timeStep)
                self._drawPlayers(positions)
        self._lastDrawnTimeStep = timeStep

    # def paintEvent(self, event):
    #     if self._backgroundCanvas is not None:
    #         canvasPainter = QPainter(self)
    #         # canvasPainter.drawImage(self.rect(), self._backgroundCanvas, self._backgroundCanvas.rect())
    #         canvasPainter.drawRect(20, 20, 10, 10)

    # canvasPainter = QPainter(self._backgroundCanvas)
    # canvasPainter.drawImage(self._backgroundCanvas.rect(), self._foregroundCanvas, self._foregroundCanvas.rect())

    # self._painter.begin(self)
    # self._drawWallsAndDoors()
    # if self._missionMetadata:
    #     if self._currentTimeStep < 0:
    #
    #         self._drawInitialVictimsAndRubbles()
    #
    #     self._updateMap()
    #
    # # if self._show_grid:
    # #     draw_grid(self._map_bounds.x1 * self._block_size, self._map_bounds.y1 * self._block_size,
    # #               self._map_bounds.x2 * self._block_size, self._map_bounds.y2 * self._block_size,
    # #               self._block_size)
    # self._painter.end()

    # def minimumSizeHint(self):
    #     return QSize(self._block_size * self._map_bounds.width() + self.margin,
    #                  self._block_size * (self._map_bounds.height() + 2) + self.margin)

    def _drawWallsAndDoors(self, gridMap: np.ndarray):
        for i in range(gridMap.shape[0]):
            for j in range(gridMap.shape[1]):
                if gridMap[i][j] == MapParser.WALL:
                    drawWall(self._scene, j, i, self._blockSize, self._blockSize)
                elif gridMap[i][j] == MapParser.DOOR:
                    drawBlock(self._scene, j, i, self._blockSize, self._blockSize, Qt.magenta)
                else:
                    drawBlock(self._scene, j, i, self._blockSize, self._blockSize, Qt.white)

    def _drawInitialVictimsAndRubbles(self):
        pass

    def _placePlayersInTheMap(self):
        positions = self._getPlayersPositionsAt(0)
        self._drawPlayers(positions)

        # Initialize trajectories
        redPen = QPen(Qt.red, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        redPath = QPainterPath()
        redPath.moveTo(self._blockSize * (positions[0][0] + 0.5), self._blockSize * (positions[0][1] + 0.5))

        greenPen = QPen(Qt.green, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        greenPath = QPainterPath()
        greenPath.moveTo(self._blockSize * (positions[1][0] + 0.5), self._blockSize * (positions[1][1] + 0.5))

        bluePen = QPen(Qt.blue, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        bluePath = QPainterPath()
        bluePath.moveTo(self._blockSize * (positions[2][0] + 0.5), self._blockSize * (positions[2][1] + 0.5))

        self._playersPathItems = [
            self._scene.addPath(redPath, redPen),
            self._scene.addPath(greenPath, greenPen),
            self._scene.addPath(bluePath, bluePen)
        ]

        self._playersPaths = [[redPath, greenPath, bluePath]]

    def _translatePosition(self, x: int, y: int) -> Tuple[int, int]:
        return x - self._mapMetadata["min_x"], y - self._mapMetadata["min_y"]

    def _drawPlayers(self, positions: List[Tuple[float, float]]):
        self._currPlayersBlocks.append(
            drawCircle(self._scene, *positions[0], self._blockSize, self._playerSize, Qt.red))
        self._currPlayersBlocks.append(
            drawCircle(self._scene, *positions[1], self._blockSize, self._playerSize, Qt.green))
        self._currPlayersBlocks.append(
            drawCircle(self._scene, *positions[2], self._blockSize, self._playerSize, Qt.blue))

    def _getPlayersPositionsAt(self, time_step: int) -> List[Tuple[float, float]]:
        positions = []
        for positionPerPlayer in self._playersPositions:
            position = positionPerPlayer[time_step]
            positions.append(self._translatePosition(position[0], position[1]))

        return positions

    def _erasePlayersBlocks(self):
        for item in self._currPlayersBlocks:
            self._scene.removeItem(item)
        self._currPlayersBlocks = []

    def _drawTrajectories(self, previous_positions: List[Tuple[float, float]], positions: List[Tuple[float, float]]):
        newPaths = []
        for i in range(len(self._playersPathItems)):
            path = QPainterPath(self._playersPaths[-1][i])
            path.lineTo(self._blockSize * (positions[i][0] + 0.5), self._blockSize * (positions[i][1] + 0.5))
            newPaths.append(path)
            self._playersPathItems[i].setPath(path)
        self._playersPaths.append(newPaths)

        # path = self._playersPathItems[0].path()
        # path.lineTo(self._blockSize * positions[0][0] + 0.5, self._blockSize * positions[0][1] + 0.5)
        # self._playersPathItems[0].setPath(path)
        #
        # # redLine = drawLine(self._scene, previous_positions[0][0] + 0.5, previous_positions[0][1] + 0.5,
        # #                    positions[0][0] + 0.5, positions[0][1] + 0.5, self._blockSize, Qt.red)
        # greenLine = drawLine(self._scene, previous_positions[1][0] + 0.5, previous_positions[1][1] + 0.5,
        #                      positions[1][0] + 0.5, positions[1][1] + 0.5, self._blockSize, Qt.green)
        # blueLine = drawLine(self._scene, previous_positions[2][0] + 0.5, previous_positions[2][1] + 0.5,
        #                     positions[2][0] + 0.5, positions[2][1] + 0.5, self._blockSize, Qt.blue)
        # self._trajectories.append([greenLine, blueLine])

    def _popTrajectories(self):
        self._playersPaths.pop()
        for i in range(len(self._playersPathItems)):
            path = self._playersPaths[-1][i]
            self._playersPathItems[i].setPath(path)

        # for item in self._trajectories[-1]:
        #     self._scene.removeItem(item)
        # self._trajectories.pop()
        #
        # path = self._playersPathItems[0].path()
        # path.pop()
        # self._playersPathItems[0].setPath(path)
