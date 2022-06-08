from enum import Enum


class SwarmConnectivityLevel(Enum):
    FULLY_CONNECTED = 1
    PARTIALLY_CONNECTED = 2
    CENTRALIZED = 3
