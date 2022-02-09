from typing import Tuple, Set
import os

import json
import numpy as np

from PreProcessing.Block import Block


class MapParser:

    WALL = 1
    DOOR = 2

    def __init__(self, mapFilepath: str, blocksFilepath: str):
        self._mapFilepath = mapFilepath
        self._blocksFilepath = blocksFilepath
        self._mapGrid = np.array([])

    def save(self, outDir: str):
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        np.savetxt(f"{outDir}/map_grid.txt", self._mapGrid, fmt="%i")

    def parse(self) -> np.ndarray:
        wallBlocks, doorBlocks = self._getStaticBlocks()

        # Get map bounds
        minX = None
        minY = None
        maxX = None
        maxY = None
        for block in wallBlocks:
            minX = block.x if minX is None else min(minX, block.x)
            minY = block.y if minY is None else min(minY, block.y)
            maxX = block.x if maxX is None else max(maxX, block.x)
            maxY = block.y if maxY is None else max(maxY, block.y)

        width = maxX - minX + 1
        height = maxY - minY + 1
        self._mapGrid = np.zeros((height, width), dtype=np.int8)

        for block in wallBlocks:
            self._mapGrid[block.y - minY][block.x - minX] = MapParser.WALL

        for block in doorBlocks:
            self._mapGrid[block.y - minY][block.x - minX] = MapParser.DOOR

    def _getStaticBlocks(self) -> Tuple[Set[Block], Set[Block]]:
        with open(self._mapFilepath, 'r') as f:
            mapJson = json.load(f)

            rooms = {}
            roomParts = {}
            roomBlocks = set()
            for location in mapJson["locations"]:
                if "child_locations" in location:
                    rooms[location["id"]] = {"parts": location["child_locations"]}
                else:
                    coordinates = location["bounds"]["coordinates"]
                    x1 = coordinates[0]["x"]
                    y1 = coordinates[0]["z"]
                    x2 = coordinates[1]["x"]
                    y2 = coordinates[1]["z"]
                    bounds = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                    if "_part" in location["type"]:
                        roomParts[location["id"]] = {"bounds": bounds}
                    else:
                        for x in range(x1 - 1, x2 + 1, 1):
                            roomBlocks.add(Block(x, y1 - 1))
                            roomBlocks.add(Block(x, y2))
                        for y in range(y1 - 1, y2 + 1, 1):
                            roomBlocks.add(Block(x1 - 1, y))
                            roomBlocks.add(Block(x2, y))

            # For each room that has parts, compute the blocks that define the contour of the room
            for _, room in rooms.items():
                if "parts" in room:
                    emptyBlocks = set()
                    wallBlocks = set()
                    for part_id in room["parts"]:
                        x1 = roomParts[part_id]["bounds"]["x1"]
                        y1 = roomParts[part_id]["bounds"]["y1"]
                        x2 = roomParts[part_id]["bounds"]["x2"]
                        y2 = roomParts[part_id]["bounds"]["y2"]

                        for x in range(x1, x2):
                            for y in range(y1, y2):
                                emptyBlocks.add(Block(x, y))

                        for x in range(x1 - 1, x2 + 1, 1):
                            wallBlocks.add(Block(x, y1 - 1))
                            wallBlocks.add(Block(x, y2))
                        for y in range(y1 - 1, y2 + 1, 1):
                            wallBlocks.add(Block(x1 - 1, y))
                            wallBlocks.add(Block(x2, y))

                    roomBlocks = roomBlocks.union(wallBlocks.difference(emptyBlocks))

            # Add connections to the openings
            doorBlocks = set()
            openingBlocks = set()
            for location in mapJson["connections"]:
                coordinates = location["bounds"]["coordinates"]
                x1 = coordinates[0]["x"]
                y1 = coordinates[0]["z"]
                x2 = coordinates[1]["x"]
                y2 = coordinates[1]["z"]

                if "door" in location["type"]:
                    for x in range(x1, x2):
                        for y in range(y1, y2):
                            doorBlocks.add(Block(x, y))
                else:
                    for x in range(x1, x2):
                        for y in range(y1, y2):
                            openingBlocks.add(Block(x, y))

            roomBlocks = roomBlocks.difference(openingBlocks)

            return roomBlocks, doorBlocks


if __name__ == "__main__":
    parser = MapParser("../data/maps/Saturn_2.1_3D_sm_v1.0.json", "")
    parser.parse()
    parser.save("../data/post_processed")