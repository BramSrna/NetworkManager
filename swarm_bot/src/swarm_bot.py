from common.src.message_types import MessageTypes
from swarm_bot.src.message_channel.message_channel_user import MessageChannelUser
from random import randint

from swarm_bot.src.message_channel.local_message_channel import LocalMessageChannel


class SwarmBot(MessageChannelUser):
    def __init__(self):
        self.id = id(self)

        self.swarm_bots = []
        
        self.curr_task = None
        self.run_logs = []

        self.sensors = {}

        self.memory = {}

        self.msg_channels = {}

    def get_id(self) -> int:
        return self.id

    def define_data_flow(self, sensor_id: str, data_flow: list) -> None:
        if sensor_id not in self.sensors:
            raise Exception("ERROR: unknown sensor: " + str(sensor_id))

        for bot_id in data_flow:
            if (bot_id not in self.swarm_bots) and (bot_id != self.get_id()):
                raise Exception("ERROR: unknown swarm bot: " + str(bot_id))
                
        self.sensors[sensor_id] = data_flow

    def connect_to_swarm_bot(self, new_swarm_bot: "SwarmBot") -> None:
        bot_id = new_swarm_bot.get_id()
        if not bot_id in self.swarm_bots:
            self.msg_channels[bot_id] = LocalMessageChannel(self, new_swarm_bot)
            self.swarm_bots.append(bot_id)

    def is_connected_to(self, swarm_bot_id: str) -> bool:
        return swarm_bot_id in self.swarm_bots

    def get_connections(self) -> list:
        return self.swarm_bots

    def receive_message(self, sender_id: str, message_type: MessageTypes, message_payload: dict) -> None:
        if message_type == MessageTypes.SENSOR_VAL:
            sender_id = sender_id
            sensor_id = message_payload["SENSOR_ID"]
            data = message_payload["DATA"]

            self.write_to_memory(sender_id, sensor_id, data)
        else:
            raise Exception("ERROR: Unknown or unhandled message type: " + str(message_type))

    def send_message(self, target_bot_id: str, message_type: MessageTypes, message_payload: dict) -> None:
        self.msg_channels[target_bot_id].send_message(message_type, message_payload)

    def add_sensor(self, sensor_id: str) -> None:
        self.sensors[sensor_id] = []

    def read_from_sensor(self, sensor_id: str) -> int:
        new_val = randint(1, 10)
        data_flow = self.sensors[sensor_id]
        for id in data_flow:
            if id == self.id:
                self.write_to_memory(self.get_id(), sensor_id, new_val)
            else:
                self.send_message(id, MessageTypes.SENSOR_VAL, {"SENSOR_ID": sensor_id, "DATA": new_val})
        return new_val

    def read_from_memory(self, swarm_bot_id: str, sensor_id: str) -> list:
        return self.memory[swarm_bot_id][sensor_id]

    def write_to_memory(self, bot_id, sensor_id, new_val):
        if bot_id not in self.memory:
            self.memory[bot_id] = {}
        if sensor_id not in self.memory[bot_id]:
            self.memory[bot_id][sensor_id] = []
        self.memory[bot_id][sensor_id].append(new_val)