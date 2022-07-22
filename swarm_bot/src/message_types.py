from enum import Enum


class MessageTypes(Enum):
    SENSOR_VAL = 1
    PATH_CHECK = 2
    MSG_RESPONSE = 3
    PROPAGATION_DEAD_END = 4
    NEW_TASK = 5
    REQUEST_TASK_TRANSFER = 6
    BASIC_PROPAGATION_MESSAGE = 7
    SYNC_MESSAGES = 8
