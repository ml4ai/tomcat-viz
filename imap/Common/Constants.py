from enum import Enum


class Constants:
    NUM_ROLES = 3

    # Players
    class Player(Enum):
        RED = 0
        GREEN = 1
        BLUE = 2

    PLAYER_COLOR_MAP = {
        "red": Player.RED,
        "green": Player.GREEN,
        "blue": Player.BLUE,
    }

    # Actions
    class Action(Enum):
        NONE = -1
        CARRYING_VICTIM = 0
        HEALING_VICTIM = 1
        DESTROYING_RUBBLE = 2
