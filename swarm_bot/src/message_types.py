from enum import Enum


class MessageTypes(Enum):
    SENSOR_VAL = 1
    MSG_RESPONSE = 2
    NEW_TASK = 3
    REQUEST_TASK_TRANSFER = 4
    BASIC_PROPAGATION_MESSAGE = 5
    SYNC_MESSAGES = 6
