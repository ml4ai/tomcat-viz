import os
from enum import Enum
from typing import List, Tuple
import numpy as np
import json
import csv
from pkg_resources import resource_stream
import codecs

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt, QGraphicsView, QPainterPath, QPen

from imap.Gui.CustomScene import CustomScene
from imap.Parser.Map import Map
from imap.Parser.Trial import Trial


class MapWidget(QWidget):
    class DrawingDirection(Enum):
        NEXT = 0
        PREVIOUS = 1

    def __init__(self, width: int, height: int, blockSize: int = 10, playerSize: int = 8):
        super().__init__()
        self._blockSize = blockSize
        self._playerSize = playerSize

        self._scene = CustomScene(0, 0, width, height, Qt.white)
        self._view = QGraphicsView(self._scene, self)

        self._map = None
        self._trial = None

        self._lastDrawnTimeStep = -1

        # Stores objects draw per time step
        self._currPlayersBlocks = []
        self._playersPaths = []
        self._playersPathItems = []
        self._markerItems = []

    def loadMap(self, mapObject: Map):
        self._map = mapObject
        self._scene.clear()
        self._drawWallsAndDoors()

    def loadTrial(self, trial: Trial):
        self._trial = trial
        self._drawInitialVictimsAndRubbles()
        self._placePlayersInTheMap()
        self._lastDrawnTimeStep = 0

    def updateFor(self, timeStep: int):
        if timeStep > self._lastDrawnTimeStep:
            for t in range(self._lastDrawnTimeStep + 1, timeStep + 1):
                self._erasePlayersBlocks()
                positions = self._getPlayersPositionsAt(t)
                self._drawTrajectories(positions)
                self._drawPlayers(positions)
                self._drawMarkers(timeStep)
        else:
            for t in range(self._lastDrawnTimeStep - 1, timeStep - 1, -1):
                self._erasePlayersBlocks()
                self._popTrajectories()
                positions = self._getPlayersPositionsAt(timeStep)
                self._drawPlayers(positions)
                self._popMarkers()
        self._lastDrawnTimeStep = timeStep

    def _drawWallsAndDoors(self):
        for i in range(self._map.grid.shape[0]):
            for j in range(self._map.grid.shape[1]):
                if self._map.grid[i][j] == Map.WALL:
                    self._scene.drawWall(j, i, self._blockSize, self._blockSize)
                elif self._map.grid[i][j] == Map.DOOR:
                    self._scene.drawDoor(j, i, self._blockSize, self._blockSize)
                else:
                    self._scene.drawEmptyBlock(j, i, self._blockSize, self._blockSize)

    def _drawInitialVictimsAndRubbles(self):
        objects_resource = resource_stream("imap.Resources.Maps", self._trial.metadata["map_block_filename"])
        utf8_reader = codecs.getreader("utf-8")
        csv_reader = csv.reader(utf8_reader(objects_resource))
        for i, row in enumerate(csv_reader):
            if i == 0:
                # Skip header
                continue

            coordinates = row[0].split()
            x, y = self._translatePosition(int(coordinates[0]), int(coordinates[2]))
            if row[1] == "block_signal_victim":
                self._scene.drawVictimSignalBlock(x, y, self._blockSize, self._blockSize)
            elif row[1] == "gravel":
                self._scene.drawGravel(x, y, self._blockSize, self._blockSize)
            elif row[1] == "block_victim_1":
                self._scene.drawVictimA(x, y, self._blockSize, self._blockSize)
            elif row[1] == "block_victim_1b":
                self._scene.drawVictimB(x, y, self._blockSize, self._blockSize)
            elif row[1] == "block_victim_proximity":
                self._scene.drawCriticalVictim(x, y, self._blockSize, self._blockSize)
            elif row[1] == "block_rubble_collapse":
                self._scene.drawRubbleCollapseBlock(x, y, self._blockSize, self._blockSize)

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
        return x - self._map.metadata["min_x"], y - self._map.metadata["min_y"]

    def _drawPlayers(self, positions: List[Tuple[float, float]]):
        self._currPlayersBlocks.append(
            self._scene.drawRed(*positions[0], self._blockSize, self._playerSize))
        self._currPlayersBlocks.append(
            self._scene.drawGreen(*positions[1], self._blockSize, self._playerSize))
        self._currPlayersBlocks.append(
            self._scene.drawBlue(*positions[2], self._blockSize, self._playerSize))

    def _getPlayersPositionsAt(self, time_step: int) -> List[Tuple[float, float]]:
        positions = []
        for positionPerPlayer in self._trial.playersPositions:
            position = positionPerPlayer[time_step]
            positions.append(self._translatePosition(position[0], position[1]))

        return positions

    def _erasePlayersBlocks(self):
        for item in self._currPlayersBlocks:
            self._scene.removeItem(item)
        self._currPlayersBlocks = []

    def _drawTrajectories(self, positions: List[Tuple[float, float]]):
        newPaths = []
        for i in range(len(self._playersPathItems)):
            path = QPainterPath(self._playersPaths[-1][i])
            path.lineTo(self._blockSize * (positions[i][0] + 0.5), self._blockSize * (positions[i][1] + 0.5))
            newPaths.append(path)
            self._playersPathItems[i].setPath(path)
        self._playersPaths.append(newPaths)

    def _popTrajectories(self):
        self._playersPaths.pop()
        for i in range(len(self._playersPathItems)):
            path = self._playersPaths[-1][i]
            self._playersPathItems[i].setPath(path)

    def _drawMarkers(self, timeStep: int):
        items = []
        for marker in self._trial.placedMarkers[timeStep]:
            items.append(self._scene.drawMarker(marker[0], marker[1], marker[2], self._blockSize, self._blockSize))
        self._markerItems.append(items)

    def _popMarkers(self):
        for marker in self._markerItems[-1]:
            self._scene.removeItem(marker)
        self._markerItems.pop()
