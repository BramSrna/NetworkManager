from common.src.message_types import MessageTypes
from http_mock.src.http_communicator import HttpCommunicator
from random import randint


class SwarmBot(HttpCommunicator):
    def __init__(self, http_mock):
        self.id = id(self)

        self.http_mock = http_mock
        self.http_mock.add_http_communicator(self)
        
        self.curr_task = None
        self.run_logs = []

        self.sensors = {}

    def get_id(self):
        return self.id

    def execute_curr_task(self, num_iterations):
        for _ in range(num_iterations):
            self.run_logs.append(self.curr_task())

    def receive_message(self, sender_id, message_type, message_payload):
        if message_type == MessageTypes.NEW_DATA_FLOW:
            sensor_id = message_payload["SENSOR_ID"]
            data_flow = message_payload["DATA_FLOW"]
            self.sensors[sensor_id] = data_flow
        else:
            raise Exception("ERROR: Unknown or undandled message type: " + str(message_type))

    def send_message(self, target_bot_id, message_type, message_payload):
        self.http_mock.send_message(self.id, target_bot_id, message_type, message_payload)

    def add_sensor(self, sensor_id):
        self.sensors[sensor_id] = []

    def read_from_sensor(self, sensor_id):
        new_val = randint(1, 10)
        data_flow = self.sensors[sensor_id]
        for id in data_flow:
            if id == self.id:
                self.memory.append(new_val)
            else:
                self.send_message(id, MessageTypes.SENSOR_VAL, {"SENSOR_ID": sensor_id, "DATA": new_val})
        return new_val