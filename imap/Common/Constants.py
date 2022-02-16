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

    # Colors
    class Colors(Enum):
        RED_PLAYER = "#E30B21"
        GREEN_PLAYER = "#13F000"
        BLUE_PLAYER = "#0045FA"
        VICTIM_A = "#02B860"
        VICTIM_B = "#02B860"
        CRITICAL_VICTIM = "#FACC09"
        SAFE_VICTIM = "#0AB7FC"
        THREAT_ACTIVATION = "#8400EB"
        RUBBLE = "#E30B21"
        MARKER = "#E602D5"
