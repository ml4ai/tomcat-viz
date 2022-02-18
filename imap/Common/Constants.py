from enum import Enum
from PyQt5.Qt import QFont


class Constants:
    NUM_ROLES = 3

    class Player(Enum):
        RED = 0
        GREEN = 1
        BLUE = 2

    PLAYER_COLOR_MAP = {
        "red": Player.RED,
        "green": Player.GREEN,
        "blue": Player.BLUE,
    }

    class Action(Enum):
        NONE = -1
        CARRYING_VICTIM = 0
        HEALING_VICTIM = 1
        DESTROYING_RUBBLE = 2

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
        INCONSISTENCY = "#FA8B03"

    # TODO - remove?
    class BlockType(Enum):
        RUBBLE = 0
        MARKER = 1
        VICTIM_A = 2
        VICTIM_B = 3
        CRITICAL_VICTIM = 4
        SAFE_VICTIM = 5

    class MarkerType(Enum):
        NO_VICTIM = 0
        VICTIM_A = 1
        VICTIM_B = 2
        REGULAR_VICTIM = 3
        CRITICAL_VICTIM = 4
        THREAT_ROOM = 5
        SOS = 6

    class VictimType(Enum):
        A = 0
        B = 1
        CRITICAL = 2
        SAFE_A = 3
        SAFE_B = 4
        SAFE_CRITICAL = 5

    class EquippedItem(Enum):
        NONE = 0

    class Font(Enum):
        TINY_REGULAR = QFont("Helvetica", 10)
        SMALL_BOLD = QFont("Helvetica", 14, QFont.Bold)
        SMALL_REGULAR = QFont("Helvetica", 14)
        LARGE_BOLD = QFont("Helvetica", 40)




