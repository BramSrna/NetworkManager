from swarm_bot.src.swarm_bot import SwarmBot
from common.src.message_types import MessageTypes
from http_mock.src.http_communicator import HttpCommunicator

class ControlCentre(HttpCommunicator):
    def __init__(self, http_mock):
        self.id = id(self)

        self.http_mock = http_mock
        self.http_mock.add_http_communicator(self)

        self.swarm_bots = []
        self.run_logs = {}

        self.memory = {}

    def get_id(self):
        return self.id

    def add_swarm_bot(self, new_swarm_bot):
        if not isinstance(new_swarm_bot, SwarmBot):
            raise Exception("ERROR: new_swarm_bot must be of type SwarmBot")
        bot_id = new_swarm_bot.get_id()
        self.swarm_bots.append(bot_id)

    def define_data_flow(self, swarm_bot_id, sensor_id, data_flow):
        self.send_message(swarm_bot_id, MessageTypes.NEW_DATA_FLOW, {"SENSOR_ID": sensor_id, "DATA_FLOW": data_flow})

    def send_message(self, target_bot_id, message_type, message_payload):
        self.http_mock.send_message(self.id, target_bot_id, message_type, message_payload)

    def receive_message(self, sender_id, message_type, message_payload):
        if message_type == MessageTypes.SENSOR_VAL:
            sender_id = sender_id
            sensor_id = message_payload["SENSOR_ID"]
            data = message_payload["DATA"]
            if sender_id not in self.memory:
                self.memory[sender_id] = {}
            if sensor_id not in self.memory[sender_id]:
                self.memory[sender_id][sensor_id] = []
            self.memory[sender_id][sensor_id].append(data)
        else:
            raise Exception("ERROR: Unknown or undandled message type: " + str(message_type))

    def get_run_logs(self, swarm_bot_id):
        self.send_message(swarm_bot_id, MessageTypes.LOG_REQUEST, {})
        return self.run_logs[swarm_bot_id]

    def read_from_memory(self, swarm_bot_id, sensor_id):
        return self.memory[swarm_bot_id][sensor_id]