import threading

from swarm_bot.src.message_types import MessageTypes
from swarm_bot.src.message_channel.message_channel_user import MessageChannelUser

from swarm_bot.src.message_format.local_message_format import LocalMessageFormat
from swarm_bot.src.message_format.message_format import MessageFormat
from swarm_bot.src.executor_interface import ExecutorInterface


class SwarmBot(MessageChannelUser):
    def __init__(self):
        self.id = id(self)

        self.sensors = {}
        self.memory = {}
        self.data_flows = {}

        self.msg_channels = {}

        self.msg_inbox = {}

        self.MSG_RESPONSE_TIMEOUT_LIMIT = 10

        self.assigned_task = None
        self.task_queue = []

        self.task_execution_history = []

        self.run_task_executor_loop = threading.Event()

        self.startup()

    def teardown(self):
        self.run_task_executor_loop.set()
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

        self.data_flows[sensor_id] = data_flow

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
        print("Received message. receiver bot ID: {}, target bot ID: {}, message ID {}, message type {}, payload: {}\n\n".format(self.get_id(), message.get_target_bot_id(), message.get_id(), message.get_message_type(), message.get_message_payload()))

        target_id = message.get_target_bot_id()

        if (target_id != self.get_id()) and (target_id is not None):
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
            elif message_type == MessageTypes.NEW_TASK:
                self.handle_new_task_message(message)
            elif message_type == MessageTypes.REQUEST_TASK_TRANSFER:
                message_payload = message.get_message_payload()
                task = None
                task_id = message_payload["TASK_ID"]
                for i in range(len(self.task_queue)):
                    curr_task = self.task_queue[i]
                    if ("TASK" in curr_task) and (curr_task["TASK"].get_id() == task_id):
                        task = curr_task["TASK"]
                        break
                    i += 1
                if task is not None:
                    self.task_queue.pop(i)
                self.create_message(message.get_original_sender_id(), MessageTypes.MSG_RESPONSE, {"ORIG_MSG_ID": message.get_id(), "TASK": task}, False)
            elif message_type == MessageTypes.PROPAGATION_DEAD_END:
                pass
            else:
                raise Exception("ERROR: Unknown message type: " + str(message_type))

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

        num_msgs_to_send = 0

        for bot_id in targets:
            if bot_id not in message.get_intermediaries():
                num_msgs_to_send += 1

        if num_msgs_to_send == 0:
            self.create_message(message.get_propagator_id(), MessageTypes.PROPAGATION_DEAD_END, {"ORIG_MSG_ID": message.get_id()}, False)
        elif sync_message:
            self.msg_inbox[message.get_id()] = {"RESPONSE_FLAG": threading.Event(), "NUM_REMAINING_RESPONSES": num_msgs_to_send, "RESPONSES": []}

        msg_threads = []

        for bot_id in targets:
            if bot_id not in message.get_intermediaries():
                message.add_intermediary(self.get_id())
                print("Sent message. Sender bot ID: {}, target bot ID: {}, message ID {}, message type: {}, sender message inbox {}\n\n".format(self.get_id(), target_bot_id, message.get_id(), message.get_message_type(), self.msg_inbox))
                thread = threading.Thread(target=self.msg_channels[bot_id].send_message, args=(message,))
                thread.start()
                msg_threads.append(thread)

        if sync_message:
            resp_flag = self.msg_inbox[message.get_id()]["RESPONSE_FLAG"]
            while (not resp_flag.is_set()):
                resp_flag_set = resp_flag.wait(self.MSG_RESPONSE_TIMEOUT_LIMIT)
                if not resp_flag_set:
                    return []
                else:
                    if self.msg_inbox[message.get_id()]["NUM_REMAINING_RESPONSES"] > 0:
                        resp_flag.clear()
            return self.msg_inbox[message.get_id()]["RESPONSES"]

    def add_sensor(self, sensor) -> None:
        self.sensors[sensor.get_id()] = sensor

    def read_from_sensor(self, sensor_id: str, additional_params) -> int:
        read_val = self.sensors[sensor_id].read_from_sensor(additional_params)

        if sensor_id in self.data_flows:
            data_flow = self.data_flows[sensor_id]
            for id in data_flow:
                if id == self.id:
                    self.write_to_memory(self.get_id(), sensor_id, read_val)
                else:
                    self.create_message(id, MessageTypes.SENSOR_VAL, {"SENSOR_ID": sensor_id, "DATA": read_val}, False)

        return read_val

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

    def get_assigned_task(self):
        return self.assigned_task

    def task_executor_loop(self):
        while (not self.run_task_executor_loop.is_set()):
            if not self.run_task_executor_loop.is_set():
                if len(self.task_queue) > 0:
                    next_task = None
                    while next_task is None:
                        next_task_info = self.task_queue.pop(0)
                        if "TASK" in next_task_info:
                            next_task = next_task_info["TASK"]
                        else:
                            responses = self.create_message(next_task_info["HOLDER_ID"], MessageTypes.REQUEST_TASK_TRANSFER, {"TASK_ID": next_task_info["TASK_ID"]}, True)
                            target_response = responses[0].get_message_payload()
                            next_task = target_response["TASK"]
                    self.assigned_task = next_task

                    self.task_execution_history.append(self.assigned_task)
                    executor_interface = ExecutorInterface(self)
                    self.assigned_task.set_executor_interface(executor_interface)
                    curr_execution = 0
                    max_executions = 10000
                    while (not self.assigned_task.is_task_complete()) and (curr_execution < max_executions):
                        self.assigned_task.execute_task()
                        curr_execution += 1
                    self.assigned_task = None

    def handle_new_task_message(self, message):
        message_payload = message.get_message_payload()

        self.task_queue.append({"HOLDER_ID": message_payload["TASK_HOLDER"], "TASK_ID": message_payload["TASK_ID"]})

    def receive_task(self, new_task):
        self.task_queue.append({"TASK": new_task})
        if len(self.task_queue) > 1:
            self.create_message(None, MessageTypes.NEW_TASK, {"TASK_ID": new_task.get_id(), "TASK_HOLDER": self.get_id()}, False)

    def get_task_queue(self):
        return self.task_queue

    def get_task_execution_history(self):
        return self.task_execution_history

    def startup(self):
        thread = threading.Thread(target=self.task_executor_loop)
        thread.start()
