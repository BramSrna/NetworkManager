from enum import Enum


class MessageTypes(Enum):
    NEW_DATA_FLOW = 1
    SENSOR_VAL = 2
    PATH_CHECK = 3
    MSG_RESPONSE = 4
    PROPAGATION_DEAD_END = 5
