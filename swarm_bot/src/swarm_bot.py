from common.src.message_types import MessageTypes
from http_mock.src.http_communicator import HttpCommunicator
from random import randint


class SwarmBot(HttpCommunicator):
    def __init__(self):
        self.id = id(self)

        self.http_mock = None

        self.swarm_bots = []
        
        self.curr_task = None
        self.run_logs = []

        self.sensors = {}

        self.memory = {}

    def set_http_mock(self, new_http_mock):
        self.http_mock = new_http_mock
        self.http_mock.add_http_communicator(self)

    def get_id(self):
        return self.id

    def define_data_flow(self, sensor_id, data_flow):
        for bot_id in data_flow:
            if bot_id not in self.swarm_bots:
                raise Exception("ERROR: unknown swarm bot: " + str(bot_id))
        self.sensors[sensor_id] = data_flow

    def connect_to_swarm_bot(self, new_swarm_bot):
        if not isinstance(new_swarm_bot, SwarmBot):
            raise Exception("ERROR: new_swarm_bot must be of type SwarmBot")
        bot_id = new_swarm_bot.get_id()
        if not bot_id in self.swarm_bots:
            self.swarm_bots.append(bot_id)

    def execute_curr_task(self, num_iterations):
        for _ in range(num_iterations):
            self.run_logs.append(self.curr_task())

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

    def read_from_memory(self, swarm_bot_id, sensor_id):
        print(self.memory)
        return self.memory[swarm_bot_id][sensor_id]