from enum import Enum
from typing import Dict, List
import csv
from pkg_resources import resource_stream
import codecs

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt, QGraphicsView, QPainterPath, QPen, QGraphicsItem

from imap.Common.Format import secondsToTime
from imap.Common.Constants import Constants
from imap.Gui.CustomScene import CustomScene
from imap.Parser.Map import Map
from imap.Parser.Trial import Trial, Position, Victim


class SceneObjectAction:
    """
    As we adding and removing objects from the scene, we store the collection so we can reverse the process
    """

    def __init__(self, item: QGraphicsItem, added: bool):
        self.item = item
        self.added = added


class MapWidget(QWidget):
    class DrawingDirection(Enum):
        NEXT = 0
        PREVIOUS = 1

    def __init__(self, width: int, height: int, blockSize: int = 10, playerSize: int = 8):
        super().__init__()
        self._blockSize = blockSize
        self._playerSize = playerSize

        self.setFixedWidth(width)
        self._scene = CustomScene(0, 0, width, height, Qt.white)
        self._view = QGraphicsView(self._scene, self)

        self._map = None
        self._trial = None

        self._lastDrawnTimeStep = -1
        self._maxDrawnTimeStep = -1

        # List of scene objects and actions (addition or removal) over time
        # Every time step will store a collection of scene object actions.
        self._sceneObjectActions: List[List[SceneObjectAction]] = [[]]

        # Stores objects draw per time step
        self._currPlayersBlocks = []
        self._playersPaths = []
        self._playersPathItems = []

        # Items added and removed to/from the scene per time step. It will cache the objects so we don't need to
        # recreate then if we go forth, back and forth
        self._addedPlayerItems = [[]]
        self._removedPlayerItems = [[]]
        self._addedBlockItems = [[]]
        self._removedBlockItems = [[]]

        # Marker item drawn in a given position
        self._markerItems: Dict[Position, QGraphicsItem] = {}

        # The number of rubbles per position (> 1 if rubbles are stacked on top of each other)
        self._rubbleCounts: Dict[Position, int] = {}

        # Rubble item drawn in a given position
        self._rubbleItems: Dict[Position, QGraphicsItem] = {}

        # Victim item drawn in a given position
        self._victimItems: Dict[Position, QGraphicsItem] = {}

    def loadMap(self, mapObject: Map):
        self._map = mapObject
        self._scene.clear()
        self._drawWallsAndDoors()

    def loadTrial(self, trial: Trial):
        self._trial = trial
        self._sceneObjectActions.append([])
        self._drawInitialVictimsAndRubbles()
        self._placePlayersInTheMap()
        self._lastDrawnTimeStep = 0
        self._maxDrawnTimeStep = 0

    def updateFor(self, timeStep: int):
        if timeStep > self._lastDrawnTimeStep:
            for t in range(self._lastDrawnTimeStep + 1, timeStep + 1):
                self._drawTrajectoriesAt(t, True)
                self._drawPlayersAt(t, True)
                self._drawBlocks(t, True)
        else:
            for t in range(self._lastDrawnTimeStep - 1, timeStep - 1, -1):
                self._drawTrajectoriesAt(t, False)
                self._drawPlayersAt(t, False)
                self._drawBlocks(t, False)

        self._lastDrawnTimeStep = timeStep
        self._maxDrawnTimeStep = max(self._maxDrawnTimeStep, timeStep)

    def reset(self):
        self._scene.clear()
        self._map = None
        self._trial = None
        self._lastDrawnTimeStep = -1
        self._maxDrawnTimeStep = -1
        self._sceneObjectActions: List[List[SceneObjectAction]] = [[]]
        self._currPlayersBlocks = []
        self._playersPaths = []
        self._playersPathItems = []
        self._addedPlayerItems = [[]]
        self._removedPlayerItems = [[]]
        self._addedBlockItems = [[]]
        self._removedBlockItems = [[]]
        self._markerItems: Dict[Position, QGraphicsItem] = {}
        self._rubbleCounts: Dict[Position, int] = {}
        self._rubbleItems: Dict[Position, QGraphicsItem] = {}
        self._victimItems: Dict[Position, QGraphicsItem] = {}

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
        self._addedBlockItems.append([])
        self._removedBlockItems.append([])
        for i, row in enumerate(csv_reader):
            if i == 0:
                # Skip header
                continue

            coordinates = row[0].split()
            x = int(coordinates[0]) - self._map.metadata["min_x"]
            y = int(coordinates[2]) - self._map.metadata["min_y"]
            position = Position(x, y)
            item = None
            if row[1] == "block_signal_victim":
                item = self._scene.drawVictimSignalBlock(x, y, self._blockSize, self._blockSize)
            elif row[1] == "gravel":
                if position in self._rubbleItems:
                    # If rubble is comprised of blocks stacked on top of each other, we only draw one and keep a counter
                    # to know how many more there are in the stack per position
                    self._rubbleCounts[position] += 1
                else:
                    item = self._scene.drawRubble(x, y, self._blockSize, self._blockSize)
                    self._rubbleCounts[position] = 1
                    self._rubbleItems[position] = item
            elif row[1] == "block_victim_1":
                item = self._scene.drawVictimA(x, y, self._blockSize, self._blockSize)
                self._victimItems[position] = item
            elif row[1] == "block_victim_1b":
                item = self._scene.drawVictimB(x, y, self._blockSize, self._blockSize)
                self._victimItems[position] = item
            elif row[1] == "block_victim_proximity":
                item = self._scene.drawCriticalVictim(x, y, self._blockSize, self._blockSize)
                self._victimItems[position] = item
            elif row[1] == "block_rubble_collapse":
                item = self._scene.drawRubbleCollapseBlock(x, y, self._blockSize, self._blockSize)

            if item is not None:
                self._addedBlockItems[0].append(item)

    def _placePlayersInTheMap(self):
        self._drawPlayersAt(0, True)
        self._initializeTrajectories()

    def _drawPlayersAt(self, timeStep: int, forward: bool):
        if forward:
            if timeStep > self._maxDrawnTimeStep:
                if len(self._addedPlayerItems) == timeStep:
                    self._addedPlayerItems.append([])
                    self._removedPlayerItems.append([])

                # Remove player items from previous time step
                if timeStep >= 1:
                    for item in self._addedPlayerItems[timeStep - 1]:
                        self._removedPlayerItems[timeStep].append(item)
                        self._scene.removeItem(item)

                # Create new items for the current time step
                # The creation of items already insert them into the canvas
                items = self._createPlayerItemsAt(timeStep)
                for item in items:
                    self._addedPlayerItems[timeStep].append(item)
            else:
                # Items were previously created. Just add and remove them accordingly
                for item in self._addedPlayerItems[timeStep]:
                    self._scene.addItem(item)

                for item in self._removedPlayerItems[timeStep]:
                    self._scene.removeItem(item)
        else:
            # Reverse the actions of the subsequent time step
            for item in self._addedPlayerItems[timeStep + 1]:
                self._scene.removeItem(item)

            for item in self._removedPlayerItems[timeStep + 1]:
                self._scene.addItem(item)

    def _createPlayerItemsAt(self, timeStep: int) -> List[QGraphicsItem]:
        items = [
            self._scene.drawRed(self._trial.playersPositions[Constants.Player.RED.value][timeStep][0],
                                self._trial.playersPositions[Constants.Player.RED.value][timeStep][1], self._blockSize,
                                self._playerSize),
            self._scene.drawGreen(self._trial.playersPositions[Constants.Player.GREEN.value][timeStep][0],
                                  self._trial.playersPositions[Constants.Player.GREEN.value][timeStep][1],
                                  self._blockSize,
                                  self._playerSize),
            self._scene.drawBlue(self._trial.playersPositions[Constants.Player.BLUE.value][timeStep][0],
                                 self._trial.playersPositions[Constants.Player.BLUE.value][timeStep][1],
                                 self._blockSize,
                                 self._playerSize)
        ]

        return items

    def _initializeTrajectories(self):
        # Initialize trajectories
        redPen = QPen(Qt.red, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        redPath = QPainterPath()
        redPath.moveTo(self._blockSize * (self._trial.playersPositions[Constants.Player.RED.value][0][0] + 0.5),
                       self._blockSize * (self._trial.playersPositions[Constants.Player.RED.value][0][1] + 0.5))

        greenPen = QPen(Qt.green, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        greenPath = QPainterPath()
        greenPath.moveTo(self._blockSize * (self._trial.playersPositions[Constants.Player.GREEN.value][0][0] + 0.5),
                         self._blockSize * (self._trial.playersPositions[Constants.Player.GREEN.value][0][1] + 0.5))

        bluePen = QPen(Qt.blue, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        bluePath = QPainterPath()
        bluePath.moveTo(self._blockSize * (self._trial.playersPositions[Constants.Player.BLUE.value][0][0] + 0.5),
                        self._blockSize * (self._trial.playersPositions[Constants.Player.BLUE.value][0][1] + 0.5))

        self._playersPathItems = [
            self._scene.addPath(redPath, redPen),
            self._scene.addPath(greenPath, greenPen),
            self._scene.addPath(bluePath, bluePen)
        ]

        self._playersPaths = [[redPath, greenPath, bluePath]]

    # def _translatePosition(self, x: int, y: int) -> Tuple[int, int]:
    #     return x - self._map.metadata["min_x"], y - self._map.metadata["min_y"]

    # def _getPlayersPositionsAt(self, time_step: int) -> List[Tuple[float, float]]:
    #     positions = []
    #     for positionPerPlayer in self._trial.playersPositions:
    #         position = positionPerPlayer[time_step]
    #         positions.append(position[0], position[1])
    #
    #     return positions

    def _drawTrajectoriesAt(self, timeStep: int, forward: bool):
        if forward:
            if timeStep > self._maxDrawnTimeStep:
                # Create a new path extending from the previous one
                paths = self._createPathTo(timeStep)
                self._playersPaths.append(paths)
            else:
                # Reuse previously created path
                paths = self._playersPaths[timeStep]
        else:
            # Reuse previously created path
            paths = self._playersPaths[timeStep]

        # Update scene to use the current path
        for i, path in enumerate(paths):
            self._playersPathItems[i].setPath(path)

    def _createPathTo(self, timeStep: int):
        paths = []
        for i, position in enumerate(self._trial.playersPositions):
            # Extend previous path
            path = QPainterPath(self._playersPaths[timeStep - 1][i])
            path.lineTo(self._blockSize * (position[timeStep][0] + 0.5),
                        self._blockSize * (position[timeStep][1] + 0.5))
            paths.append(path)

        return paths

    def _drawBlocks(self, timeStep: int, forward: bool):
        if forward:
            if timeStep > self._maxDrawnTimeStep:
                if len(self._addedBlockItems) == timeStep:
                    self._addedBlockItems.append([])
                    self._removedBlockItems.append([])

                self._drawMarkers(timeStep)
                self._drawRubble(timeStep)
                self._drawVictims(timeStep)

            else:
                for item in self._removedBlockItems[timeStep]:
                    self._scene.removeItem(item)

                for item in self._addedBlockItems[timeStep]:
                    self._scene.addItem(item)
        else:
            # Reverse the action of the next time step
            for item in self._removedBlockItems[timeStep + 1]:
                self._scene.addItem(item)

            for item in self._addedBlockItems[timeStep + 1]:
                self._scene.removeItem(item)

    def _drawMarkers(self, timeStep: int):
        self._eraseDestroyedMarkers(timeStep)
        self._drawPlacedMarkers(timeStep)

    def _eraseDestroyedMarkers(self, timeStep: int):
        for marker in self._trial.removedMarkers[timeStep]:
            if marker.position in self._markerItems:
                item = self._markerItems[marker.position]
                self._removedBlockItems[timeStep].append(item)
                self._scene.removeItem(item)
                del self._markerItems[marker.position]
            else:
                print(
                    f"[{secondsToTime(timeStep)}]: Marker {marker.markerType} at {marker.position} not found.")

    def _drawPlacedMarkers(self, timeStep: int):
        for marker in self._trial.placedMarkers[timeStep]:
            if marker.position in self._markerItems:
                # Remove old marker before adding the new one
                item = self._markerItems[marker.position]
                self._removedBlockItems[timeStep].append(item)
                self._scene.removeItem(item)

            item = self._scene.drawMarker(marker.markerType, marker.position.x, marker.position.y, self._blockSize,
                                          self._blockSize)
            self._markerItems[marker.position] = item
            self._addedBlockItems[timeStep].append(item)

    def _drawRubble(self, timeStep: int):
        for position, count in self._trial.rubbleCounts[timeStep].items():
            if position in self._rubbleCounts:
                self._rubbleCounts[position] += count

                if self._rubbleCounts[position] == 0:
                    item = self._rubbleItems[position]
                    self._scene.removeItem(item)
                    self._removedBlockItems[timeStep].append(item)
                    del self._rubbleCounts[position]
            else:
                if count > 0:
                    # Some messages are inconsistent and show rubble destroyed when there is no rubble
                    self._rubbleCounts[position] = count
                    item = self._scene.drawRubble(position.x, position.y, self._blockSize, self._blockSize)
                    self._rubbleItems[position] = item
                    self._addedBlockItems[timeStep].append(item)

    def _drawVictims(self, timeStep: int):
        self._drawSavedVictims(timeStep)
        self._drawPickedUpVictims(timeStep)
        self._drawPlacedVictims(timeStep)

    def _drawSavedVictims(self, timeStep: int):
        for victim in self._trial.savedVictims[timeStep]:
            # We only process if the victim was not picked up in the same time step, to avoid adding
            # (changing the victim to the new type) and removing it (if it's picked up) in the same time step.
            if victim.victimType == Constants.VictimType.A:
                newType = Constants.VictimType.SAFE_A
            elif victim.victimType == Constants.VictimType.B:
                newType = Constants.VictimType.SAFE_B
            else:
                newType = Constants.VictimType.SAFE_CRITICAL

            safeVictim = Victim(newType, victim.position.x, victim.position.y)
            if safeVictim in self._trial.pickedUpVictims[timeStep]:
                continue

            if victim.position in self._victimItems:
                # Remove current victim block
                item = self._victimItems[victim.position]
                self._scene.removeItem(item)
                self._removedBlockItems[timeStep].append(item)

                # Create a safe victim block in the same position.
                item = None
                if victim.victimType == Constants.VictimType.A:
                    item = self._scene.drawSafeVictimA(victim.position.x, victim.position.y, self._blockSize,
                                                       self._blockSize)
                elif victim.victimType == Constants.VictimType.B:
                    item = self._scene.drawSafeVictimB(victim.position.x, victim.position.y, self._blockSize,
                                                       self._blockSize)
                else:
                    item = self._scene.drawSafeCriticalVictim(victim.position.x, victim.position.y, self._blockSize,
                                                              self._blockSize)

                self._victimItems[victim.position] = item
                self._addedBlockItems[timeStep].append(item)
            else:
                print(
                    f"[{secondsToTime(timeStep)}]: Rescuing victim {victim.victimType} at {victim.position} not found.")
                self._scene.drawMissingVictim(victim.position.x, victim.position.y, self._blockSize, self._blockSize)

    def _drawPickedUpVictims(self, timeStep: int):
        for victim in self._trial.pickedUpVictims[timeStep]:
            if victim.position in self._victimItems:
                # Remove current victim block
                item = self._victimItems[victim.position]
                self._scene.removeItem(item)
                self._removedBlockItems[timeStep].append(item)
                del self._victimItems[victim.position]
            else:
                print(
                    f"[{secondsToTime(timeStep)}]: Picking up victim {victim.victimType} at {victim.position} not found.")
                self._scene.drawMissingVictim(victim.position.x, victim.position.y, self._blockSize, self._blockSize)

    def _drawPlacedVictims(self, timeStep: int):
        for victim in self._trial.placedVictims[timeStep]:
            item = None
            if victim.victimType == Constants.VictimType.A:
                item = self._scene.drawVictimA(victim.position.x, victim.position.y, self._blockSize,
                                               self._blockSize)
            elif victim.victimType == Constants.VictimType.B:
                item = self._scene.drawVictimB(victim.position.x, victim.position.y, self._blockSize,
                                               self._blockSize)
            elif victim.victimType == Constants.VictimType.CRITICAL:
                item = self._scene.drawCriticalVictim(victim.position.x, victim.position.y, self._blockSize,
                                                      self._blockSize)
            if victim.victimType == Constants.VictimType.SAFE_A:
                item = self._scene.drawSafeVictimA(victim.position.x, victim.position.y, self._blockSize,
                                                   self._blockSize)
            elif victim.victimType == Constants.VictimType.SAFE_B:
                item = self._scene.drawSafeVictimB(victim.position.x, victim.position.y, self._blockSize,
                                                   self._blockSize)
            elif victim.victimType == Constants.VictimType.SAFE_CRITICAL:
                item = self._scene.drawSafeCriticalVictim(victim.position.x, victim.position.y, self._blockSize,
                                                          self._blockSize)
            if item is not None:
                self._victimItems[victim.position] = item
                self._addedBlockItems[timeStep].append(item)
