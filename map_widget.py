from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QTransform
from PyQt5.QtCore import Qt, QSize
import json
from draw_grid import draw_grid
from draw_block import draw_block
from block import Block
from bounds import Bounds
import csv


class MapWidget(QWidget):
    def __init__(self, map_filepath: str, dyn_blocks_filepath: str, block_size: int = 10, show_grid: bool = True):
        super().__init__()
        self._map_filepath = map_filepath
        self._dyn_blocks_filepath = dyn_blocks_filepath
        self._block_size = block_size
        self._show_grid = show_grid
        if show_grid:
            self.margin = 50
        else:
            self.margin = 0
        self._map_bounds = self._get_map_bounds()
        self._painter = QPainter()

    def paintEvent(self, event):
        self._painter.begin(self)
        self._draw_map()
        self._draw_dynamic_blocks()
        if self._show_grid:
            draw_grid(self._map_bounds.x1 * self._block_size, self._map_bounds.y1 * self._block_size,
                      self._map_bounds.x2 * self._block_size, self._map_bounds.y2 * self._block_size, self._block_size)
        self._painter.end()

    def minimumSizeHint(self):
        return QSize(self._block_size * self._map_bounds.width() + self.margin,
                     self._block_size * (self._map_bounds.height() + 2) + self.margin)

    def _get_map_bounds(self):
        with open(self._map_filepath, 'r') as f:
            map_json = json.load(f)

            min_x = 1e9
            min_y = 1e9
            max_x = -1e9
            max_y = -1e9

            # Find the minimum x and z. They will be used to shift the map such that it starts in the top-left
            # position of the window.
            rooms = 0
            for item_type in ["locations", "connections"]:
                for item in map_json[item_type]:
                    if item["type"] == "room":
                        rooms += 1
                    if "bounds" in item:
                        x1 = item["bounds"]["coordinates"][0]["x"]
                        y1 = item["bounds"]["coordinates"][0]["z"]
                        x2 = item["bounds"]["coordinates"][1]["x"]
                        y2 = item["bounds"]["coordinates"][1]["z"]

                        min_x = min(min_x, x1)
                        min_y = min(min_y, y1)
                        max_x = max(max_x, x2)
                        max_y = max(max_y, y2)

            return Bounds(min_x - 1, min_y - 1, max_x + 1, max_y + 1)

    def _draw_map(self):
        room_blocks, door_blocks = self._parse_map()

        # Shift the coordinate system so that the map is drawn in the correct place
        transform = QTransform()
        transform.translate(-self._map_bounds.x1 * self._block_size + self.margin,
                            -self._map_bounds.y1 * self._block_size + self.margin)
        self._painter.setTransform(transform)

        for block in room_blocks:
            draw_block(self._painter, block, self._block_size, Qt.black)

        for block in door_blocks:
            draw_block(self._painter, block, self._block_size, Qt.red)

    def _parse_map(self):
        with open(self._map_filepath, 'r') as f:
            map_json = json.load(f)

            rooms = {}
            room_parts = {}
            room_blocks = set()
            for location in map_json["locations"]:
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
                        room_parts[location["id"]] = {"bounds": bounds}
                    else:
                        for x in range(x1 - 1, x2 + 1, 1):
                            room_blocks.add(Block(x, y1 - 1))
                            room_blocks.add(Block(x, y2))
                        for y in range(y1 - 1, y2 + 1, 1):
                            room_blocks.add(Block(x1 - 1, y))
                            room_blocks.add(Block(x2, y))

            # For each room that has parts, compute the blocks that define the contour of the room
            for _, room in rooms.items():
                if "parts" in room:
                    empty_blocks = set()
                    wall_blocks = set()
                    for part_id in room["parts"]:
                        x1 = room_parts[part_id]["bounds"]["x1"]
                        y1 = room_parts[part_id]["bounds"]["y1"]
                        x2 = room_parts[part_id]["bounds"]["x2"]
                        y2 = room_parts[part_id]["bounds"]["y2"]

                        for x in range(x1, x2):
                            for y in range(y1, y2):
                                empty_blocks.add(Block(x, y))

                        for x in range(x1 - 1, x2 + 1, 1):
                            wall_blocks.add(Block(x, y1 - 1))
                            wall_blocks.add(Block(x, y2))
                        for y in range(y1 - 1, y2 + 1, 1):
                            wall_blocks.add(Block(x1 - 1, y))
                            wall_blocks.add(Block(x2, y))

                    room_blocks = room_blocks.union(wall_blocks.difference(empty_blocks))

            # Add connections to the openings
            door_blocks = set()
            opening_blocks = set()
            for location in map_json["connections"]:
                coordinates = location["bounds"]["coordinates"]
                x1 = coordinates[0]["x"]
                y1 = coordinates[0]["z"]
                x2 = coordinates[1]["x"]
                y2 = coordinates[1]["z"]

                if "door" in location["type"]:
                    for x in range(x1, x2):
                        for y in range(y1, y2):
                            door_blocks.add(Block(x, y))
                else:
                    for x in range(x1, x2):
                        for y in range(y1, y2):
                            opening_blocks.add(Block(x, y))

            room_blocks = room_blocks.difference(opening_blocks)

            return room_blocks, door_blocks

    def _draw_dynamic_blocks(self):
        with open(self._dyn_blocks_filepath, 'r') as f:
            csv_reader = csv.reader(f)
            for i, row in enumerate(csv_reader):
                if i == 0:
                    # Skip header
                    continue

                coordinates = row[0].split()
                block = Block(int(coordinates[0]), int(coordinates[2]))
                if row[1] == "block_signal_victim":
                    draw_block(self._painter, block, self._block_size, Qt.green)
                elif row[1] == "gravel":
                    draw_block(self._painter, block, self._block_size, Qt.darkGray)
                elif row[1] == "block_victim_1":
                    draw_block(self._painter, block, self._block_size, Qt.darkGreen)
                elif row[1] == "block_victim_1b":
                    draw_block(self._painter, block, self._block_size, Qt.blue)
                elif row[1] == "block_victim_proximity":
                    draw_block(self._painter, block, self._block_size, Qt.darkYellow)
                elif row[1] == "block_rubble_collapse":
                    draw_block(self._painter, block, self._block_size, Qt.darkMagenta)

    def update(self, time_step: int):
        pass
