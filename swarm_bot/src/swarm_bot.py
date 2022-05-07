from common.src.message_types import MessageTypes
from http_mock.src.http_communicator import HttpCommunicator


class SwarmBot(HttpCommunicator):
    def __init__(self, http_mock):
        self.id = id(self)

        self.http_mock = http_mock
        self.http_mock.add_http_communicator(self)
        
        self.curr_task = None
        self.run_logs = []

    def get_id(self):
        return self.id

    def execute_curr_task(self, num_iterations):
        for _ in range(num_iterations):
            self.run_logs.append(self.curr_task())

    def receive_message(self, sender_id, message_type, message_payload):
        if message_type == MessageTypes.NEW_TASK:
            new_task = message_payload["TASK"]
            num_iterations = message_payload["ITERATIONS"]
            self.curr_task = new_task
            self.execute_curr_task(num_iterations)
        elif message_type == MessageTypes.LOG_REQUEST:
            self.send_message(sender_id, MessageTypes.RUN_LOGS, self.run_logs)
        else:
            raise Exception("ERROR: Unknown or undandled message type: " + str(message_type))

    def send_message(self, target_bot_id, message_type, message_payload):
        self.http_mock.send_message(self.id, target_bot_id, message_type, message_payload)