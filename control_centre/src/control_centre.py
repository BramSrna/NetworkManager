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

    def get_id(self):
        return self.id

    def add_swarm_bot(self, new_swarm_bot):
        if not isinstance(new_swarm_bot, SwarmBot):
            raise Exception("ERROR: new_swarm_bot must be of type SwarmBot")
        self.swarm_bots.append(new_swarm_bot.get_id())

    def delegate_task(self, swarm_bot_id, task, task_iterations):
        self.send_message(swarm_bot_id, MessageTypes.NEW_TASK, {"TASK": task, "ITERATIONS": task_iterations})

    def send_message(self, target_bot_id, message_type, message_payload):
        self.http_mock.send_message(self.id, target_bot_id, message_type, message_payload)

    def receive_message(self, sender_id, message_type, message_payload):
        if message_type == MessageTypes.RUN_LOGS:
            self.run_logs[sender_id] = message_payload
        else:
            raise Exception("ERROR: Unknown or undandled message type: " + str(message_type))

    def get_run_logs(self, swarm_bot_id):
        self.send_message(swarm_bot_id, MessageTypes.LOG_REQUEST, {})
        return self.run_logs[swarm_bot_id]