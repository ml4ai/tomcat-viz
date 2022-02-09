
from typing import Tuple, Set

import json

from PreProcessing.Block import Block


class MissionParser:

    def __init__(self, mapFilepath: str, blocksFilepath: str):
        self._parseMap(mapFilepath)
        self._initializeBlocks(blocksFilepath)

    def _parseMap(self, mapFilepath: str):
        minX, minY, maxX, maxY = self._getMapBounds(mapFilepath)
        wall_blocks, door_blocks, minX, minY = self._getStaticBlocks(mapFilepath)



    def _initializeBlocks(self):
        pass