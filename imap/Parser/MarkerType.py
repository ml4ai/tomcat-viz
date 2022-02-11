from enum import Enum


class MarkerType(Enum):
    NO_VICTIM = 0
    VICTIM_A = 1
    VICTIM_B = 2
    REGULAR_VICTIM = 3
    CRITICAL_VICTIM = 4
    THREAT_ROOM = 5
    SOS = 6
