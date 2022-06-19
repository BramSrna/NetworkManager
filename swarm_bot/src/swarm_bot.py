import threading

from swarm_bot.src.message_types import MessageTypes
from swarm_bot.src.message_channel.message_channel_user import MessageChannelUser
from random import randint

from swarm_bot.src.message_format.local_message_format import LocalMessageFormat
from swarm_bot.src.message_format.message_format import MessageFormat


class SwarmBot(MessageChannelUser):
    def __init__(self):
        self.id = id(self)

        self.sensors = {}
        self.memory = {}

        self.msg_channels = {}

        self.msg_inbox = {}

        self.MSG_RESPONSE_TIMEOUT_LIMIT = 10

    def teardown(self):
        for msg_id in self.msg_inbox:
            for _ in range(self.msg_inbox[msg_id]["NUM_REMAINING_RESPONSES"]):
                self.msg_inbox[msg_id]["NUM_REMAINING_RESPONSES"] -= 1
                self.msg_inbox[msg_id]["RESPONSE_FLAG"].set()

    def get_id(self) -> int:
        return self.id

    def define_data_flow(self, sensor_id: str, data_flow: list) -> None:
        if sensor_id not in self.sensors:
            raise Exception("ERROR: unknown sensor: " + str(sensor_id))

        for bot_id in data_flow:
            if (bot_id not in self.msg_channels) and (bot_id != self.get_id()):
                responses = self.create_message(bot_id, MessageTypes.PATH_CHECK, {}, True)
                path_exists = False
                for response in responses:
                    if response.get_message_type() == MessageTypes.MSG_RESPONSE:
                        path_exists = True
                if not path_exists:
                    raise Exception("ERROR: unreachable swarm bot: " + str(bot_id))

        self.sensors[sensor_id] = data_flow

    def connect_to_swarm_bot(self, new_swarm_bot: "SwarmBot") -> None:
        bot_id = new_swarm_bot.get_id()
        if bot_id not in self.msg_channels:
            from swarm_bot.src.message_channel.local_message_channel import LocalMessageChannel
            self.msg_channels[bot_id] = LocalMessageChannel(self, new_swarm_bot)
            new_swarm_bot.connect_to_swarm_bot(self)

    def is_connected_to(self, swarm_bot_id: str) -> bool:
        return swarm_bot_id in self.msg_channels

    def get_connections(self) -> list:
        return list(self.msg_channels.keys())

    def receive_message(self, message: MessageFormat) -> None:
        print("Received message. receiver bot ID: {}, target bot ID: {}, message ID {}, message type {}, payload: {}".format(self.get_id(), message.get_target_bot_id(), message.get_id(), message.get_message_type(), message.get_message_payload()))

        target_id = message.get_target_bot_id()

        if target_id != self.get_id():
            self.send_message(target_id, message, False)
        else:
            message_type = message.get_message_type()

            if message_type == MessageTypes.MSG_RESPONSE:
                pass
            elif message_type == MessageTypes.PATH_CHECK:
                self.create_message(message.get_original_sender_id(), MessageTypes.MSG_RESPONSE, {"ORIG_MSG_ID": message.get_id()}, False)
            elif message_type == MessageTypes.SENSOR_VAL:
                message_payload = message.get_message_payload()
                sender_id = message.get_original_sender_id()

                sensor_id = message_payload["SENSOR_ID"]
                data = message_payload["DATA"]

                self.write_to_memory(sender_id, sensor_id, data)

        if "ORIG_MSG_ID" in message.get_message_payload():
            orig_msg_id = message.get_message_payload()["ORIG_MSG_ID"]
            if orig_msg_id in self.msg_inbox:
                self.msg_inbox[orig_msg_id]["RESPONSES"].append(message)
                self.msg_inbox[orig_msg_id]["NUM_REMAINING_RESPONSES"] -= 1
                self.msg_inbox[orig_msg_id]["RESPONSE_FLAG"].set()

    def create_message(self, target_bot_id: int, message_type: MessageTypes, message_payload: dict, sync_message) -> None:
        new_msg = LocalMessageFormat(self.get_id(), target_bot_id, message_type, message_payload)
        return self.send_message(target_bot_id, new_msg, sync_message)

    def send_message(self, target_bot_id: int, message, sync_message) -> None:
        targets = list(self.msg_channels.keys())
        if target_bot_id in self.msg_channels:
            targets = [target_bot_id]

        if len(targets) == 0:
            return []

        msg_threads = []

        for bot_id in targets:
            if bot_id not in message.get_intermediaries():
                message.add_intermediary(self.get_id())
                thread = threading.Thread(target=self.msg_channels[bot_id].send_message, args=(message,))
                thread.start()
                msg_threads.append(thread)

        if len(msg_threads) == 0:
            self.create_message(message.get_propagator_id(), MessageTypes.PROPAGATION_DEAD_END, {"ORIG_MSG_ID": message.get_id()}, False)
        elif sync_message:
            self.msg_inbox[message.get_id()] = {"RESPONSE_FLAG": threading.Event(), "NUM_REMAINING_RESPONSES": len(msg_threads), "RESPONSES": []}
            print("Sent SYNC message. Sender bot ID: {}, target bot ID: {}, message ID {}, sender message inbox {}".format(self.get_id(), target_bot_id, message.get_id(), self.msg_inbox))

            resp_flag = self.msg_inbox[message.get_id()]["RESPONSE_FLAG"]
            while (not resp_flag.is_set()):
                resp_flag_set = resp_flag.wait(self.MSG_RESPONSE_TIMEOUT_LIMIT)
                if not resp_flag_set:
                    return []
                else:
                    if self.msg_inbox[message.get_id()]["NUM_REMAINING_RESPONSES"] > 0:
                        resp_flag.clear()
            return self.msg_inbox[message.get_id()]["RESPONSES"]

    def add_sensor(self, sensor_id: str) -> None:
        self.sensors[sensor_id] = []

    def read_from_sensor(self, sensor_id: str) -> int:
        new_val = randint(1, 10)
        data_flow = self.sensors[sensor_id]
        for id in data_flow:
            if id == self.id:
                self.write_to_memory(self.get_id(), sensor_id, new_val)
            else:
                self.create_message(id, MessageTypes.SENSOR_VAL, {"SENSOR_ID": sensor_id, "DATA": new_val}, False)
        return new_val

    def read_from_memory(self, swarm_bot_id: str, sensor_id: str) -> list:
        if swarm_bot_id in self.memory:
            if sensor_id in self.memory[swarm_bot_id]:
                return self.memory[swarm_bot_id][sensor_id]
        return []

    def write_to_memory(self, bot_id: int, sensor_id: int, new_val: object) -> None:
        if bot_id not in self.memory:
            self.memory[bot_id] = {}
        if sensor_id not in self.memory[bot_id]:
            self.memory[bot_id][sensor_id] = []
        self.memory[bot_id][sensor_id].append(new_val)
