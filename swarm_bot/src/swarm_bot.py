import threading
import time

from random import randint

from swarm_bot.src.message_types import MessageTypes
from swarm_bot.src.message_channel.message_channel_user import MessageChannelUser

from swarm_bot.src.message_wrapper.local_message_wrapper import LocalMessageWrapper
from swarm_bot.src.message_wrapper.message_wrapper import MessageWrapper
from swarm_bot.src.executor_interface import ExecutorInterface
from swarm_bot.src.propagation_strategy.naive_propagation import NaivePropagation


class SwarmBot(MessageChannelUser):
    def __init__(self):
        self.id = id(self)

        self.sensors = {}
        self.memory = {}
        self.data_flows = {}

        self.msg_channels = {}

        self.sent_messages = {}
        self.msg_inbox = {}

        self.MSG_RESPONSE_TIMEOUT_LIMIT = 10

        self.assigned_task = None
        self.task_queue = []

        self.task_execution_history = []

        self.propagation_strategy = NaivePropagation(self)

        self.run_task_executor_loop = threading.Event()

        self.num_ignored_msgs = 0

        self.idle_listeners = []

        self.num_processes = 0

        self.startup()

    def teardown(self):
        self.run_task_executor_loop.set()
        for msg_id in self.sent_messages:
            for _ in range(self.sent_messages[msg_id]["NUM_REMAINING_RESPONSES"]):
                self.sent_messages[msg_id]["NUM_REMAINING_RESPONSES"] -= 1
                self.sent_messages[msg_id]["RESPONSE_FLAG"].set()

    def get_id(self) -> int:
        return self.id

    def define_data_flow(self, sensor_id: str, data_flow: list) -> None:
        if sensor_id not in self.sensors:
            raise Exception("ERROR: unknown sensor: " + str(sensor_id))

        for bot_id in data_flow:
            if (bot_id not in self.msg_channels) and (bot_id != self.get_id()):
                raise Exception("ERROR: unknown swarm bot: " + str(bot_id))

        self.data_flows[sensor_id] = data_flow

    def connect_to_swarm_bot(self, new_swarm_bot: "SwarmBot", run_sync=True) -> None:
        bot_id = new_swarm_bot.get_id()
        if bot_id not in self.msg_channels:
            from swarm_bot.src.message_channel.local_message_channel import LocalMessageChannel
            self.msg_channels[bot_id] = LocalMessageChannel(self, new_swarm_bot)
            new_swarm_bot.connect_to_swarm_bot(self, run_sync=False)

        if run_sync:
            self.sync_with_bot(bot_id)

    def is_connected_to(self, swarm_bot_id: str) -> bool:
        return swarm_bot_id in self.msg_channels

    def get_connections(self) -> list:
        return list(self.msg_channels.keys())

    def receive_message(self, message: MessageWrapper) -> None:
        self.notify_process_state(True)

        target_id = message.get_target_bot_id()
        msg_id = message.get_id()

        print("Received message. receiver bot ID: {}, target bot ID: {}, message ID {}, message type {}, payload: {}\n\n".format(self.get_id(), message.get_target_bot_id(), msg_id, message.get_message_type(), message.get_message_payload()))

        if (msg_id in self.msg_inbox) or (msg_id in self.sent_messages):
            if msg_id not in self.msg_inbox:
                self.msg_inbox[msg_id] = {"MSG": message, "NUM_TIMES_RCVD": 0}
            self.msg_inbox[msg_id]["NUM_TIMES_RCVD"] += 1
            self.num_ignored_msgs += 1
            self.notify_process_state(False)
            return False

        if (target_id != self.get_id()) and (target_id is not None):
            self.num_ignored_msgs += 1
            self.send_message(target_id, message, False)
            self.notify_process_state(False)
            return False

        self.msg_inbox[msg_id] = {"MSG": message, "NUM_TIMES_RCVD": 1}

        message_type = message.get_message_type()

        if message_type == MessageTypes.MSG_RESPONSE:
            pass
        elif message_type == MessageTypes.PATH_CHECK:
            self.create_message(message.get_original_sender_id(), MessageTypes.MSG_RESPONSE, {"ORIG_MSG_ID": msg_id}, False)
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
            self.create_message(message.get_original_sender_id(), MessageTypes.MSG_RESPONSE, {"ORIG_MSG_ID": msg_id, "TASK": task}, False)
        elif message_type == MessageTypes.PROPAGATION_DEAD_END:
            pass
        elif message_type == MessageTypes.BASIC_PROPAGATION_MESSAGE:
            pass
        elif message_type == MessageTypes.SYNC_MESSAGES:
            message_payload = message.get_message_payload()
            id_list = message_payload["MSG_LIST"]
            missing_msgs = []

            rcvd_msg_ids = list(self.msg_inbox.keys())
            sent_msg_ids = list(self.sent_messages.keys())

            for curr_msg_id in id_list:
                if (curr_msg_id not in rcvd_msg_ids) and (curr_msg_id not in sent_msg_ids):
                    missing_msgs.append(curr_msg_id)

            self.create_message(message.get_original_sender_id(), MessageTypes.MSG_RESPONSE, {"ORIG_MSG_ID": msg_id, "MSG_LIST": missing_msgs}, False)

        elif message_type == MessageTypes.SWARM_SNAPSHOT:
            snapshot = self.get_swarm_snapshot(message=message)
            self.create_message(message.get_original_sender_id(), MessageTypes.MSG_RESPONSE, {"ORIG_MSG_ID": msg_id, "SHAPSHOT": snapshot}, False)
        else:
            raise Exception("ERROR: Unknown message type: " + str(message_type))

        if target_id is None:
            targets = self.propagation_strategy.determine_prop_targets()
            for target in targets:
                self.send_message(target, message, False)

        if "ORIG_MSG_ID" in message.get_message_payload():
            orig_msg_id = message.get_message_payload()["ORIG_MSG_ID"]
            if (orig_msg_id in self.sent_messages) and ("RESPONSES" in self.sent_messages[orig_msg_id]):
                self.sent_messages[orig_msg_id]["RESPONSES"].append(message)
                self.sent_messages[orig_msg_id]["NUM_REMAINING_RESPONSES"] -= 1
                self.sent_messages[orig_msg_id]["RESPONSE_FLAG"].set()

        if (len(self.msg_inbox.keys()) > 0) and (len(self.msg_inbox.keys()) % 10 == 0):
            bot_ids = list(self.msg_channels.keys())
            for bot_id in bot_ids:
                self.sync_with_bot(bot_id)

        self.notify_process_state(False)

    def create_message(self, target_bot_id: int, message_type: MessageTypes, message_payload: dict, sync_message) -> None:
        targets = []
        if target_bot_id is None:
            targets = self.propagation_strategy.determine_prop_targets()
        elif target_bot_id in self.msg_channels:
            targets.append(target_bot_id)
        else:
            raise Exception("ERROR: Tried to create message for unknown bot ID: " + str(target_bot_id))

        message_id = randint(0, 1000000)

        responses = []
        for target in targets:
            new_msg = LocalMessageWrapper(message_id, self.get_id(), target_bot_id, message_type, message_payload, sync_message)
            curr_response = self.send_message(target, new_msg, sync_message)
            if isinstance(curr_response, list):
                responses += curr_response
        return responses

    def send_message(self, target_bot_id: int, message, sync_message) -> None:
        self.notify_process_state(True)

        targets = list(self.msg_channels.keys())
        if target_bot_id in self.msg_channels:
            targets = [target_bot_id]

        if len(targets) == 0:
            self.notify_process_state(False)
            return []

        msg_id = message.get_id()

        if msg_id not in self.sent_messages:
            self.sent_messages[msg_id] = {"TIME_SENT": time.time(), "NUM_REMAINING_RESPONSES": 0, "SENT_MSG": message, "NUM_TIMES_SENT": 0}

        self.sent_messages[msg_id]["NUM_TIMES_SENT"] += 1

        if sync_message:
            self.sent_messages[msg_id]["RESPONSE_FLAG"] = threading.Event()
            self.sent_messages[msg_id]["NUM_REMAINING_RESPONSES"] = len(targets)
            self.sent_messages[msg_id]["RESPONSES"] = []

        msg_threads = []

        for bot_id in targets:
            print("Sent message. Sender bot ID: {}, target bot ID: {}, message ID {}, message type: {}, sender message list {}\n\n".format(self.get_id(), target_bot_id, msg_id, message.get_message_type(), self.sent_messages))
            thread = threading.Thread(target=self.msg_channels[bot_id].send_message, args=(message,))
            thread.start()
            msg_threads.append(thread)

        if sync_message:
            resp_flag = self.sent_messages[msg_id]["RESPONSE_FLAG"]
            while (not resp_flag.is_set()):
                resp_flag_set = resp_flag.wait(self.MSG_RESPONSE_TIMEOUT_LIMIT)
                if not resp_flag_set:
                    self.notify_process_state(False)
                    return []
                else:
                    if self.sent_messages[msg_id]["NUM_REMAINING_RESPONSES"] > 0:
                        resp_flag.clear()
            self.notify_process_state(False)
            return self.sent_messages[msg_id]["RESPONSES"]

        self.notify_process_state(False)

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
                    self.notify_process_state(True)
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
                    self.notify_process_state(False)

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

    def get_message_channels(self):
        return self.msg_channels

    def send_basic_propagation_message(self):
        self.create_message(None, MessageTypes.BASIC_PROPAGATION_MESSAGE, {}, False)

        latest_basic_prop_msg = None
        latest_basic_prop_msg_time = None
        for _, msg_info in self.sent_messages.items():
            msg = msg_info["SENT_MSG"]
            if msg.get_message_type() == MessageTypes.BASIC_PROPAGATION_MESSAGE:
                msg_send_time = msg_info["TIME_SENT"]
                if (latest_basic_prop_msg is None) or (msg_send_time > latest_basic_prop_msg_time):
                    latest_basic_prop_msg = msg
                    latest_basic_prop_msg_time = msg_send_time

        if latest_basic_prop_msg is None:
            return None
        return latest_basic_prop_msg.get_id()

    def received_msg_with_id(self, msg_id):
        return msg_id in self.msg_inbox

    def sync_with_bot(self, bot_id):
        if bot_id not in self.msg_channels:
            return False

        msg_list = []
        for msg_id, msg_info in self.sent_messages.items():
            if msg_info["SENT_MSG"].get_target_bot_id() is None:
                msg_list.append(msg_id)
        for msg_id, msg_info in self.msg_inbox.items():
            if msg_info["MSG"].get_target_bot_id() is None:
                msg_list.append(msg_id)

        response = self.create_message(bot_id, MessageTypes.SYNC_MESSAGES, {"MSG_LIST": msg_list}, True)
        missing_msg_list = response[0].get_message_payload()["MSG_LIST"]

        for msg_id in missing_msg_list:
            curr_msg = None
            if msg_id in self.sent_messages:
                curr_msg = self.sent_messages[msg_id]["SENT_MSG"]
            else:
                curr_msg = self.msg_inbox[msg_id]["MSG"]
            self.send_message(bot_id, curr_msg, False)

    def get_sent_messages(self):
        sent_msgs = {}
        for _, msg_info in self.sent_messages.items():
            msg_id = msg_info["SENT_MSG"].get_id()
            msg_type = msg_info["SENT_MSG"].get_message_type()
            sent_msgs[msg_id] = (msg_type, msg_info["NUM_TIMES_SENT"])
        return sent_msgs

    def get_received_messages(self):
        rcvd_msgs = {}
        for _, msg_info in self.msg_inbox.items():
            msg_id = msg_info["MSG"].get_id()
            msg_type = msg_info["MSG"].get_message_type()
            rcvd_msgs[msg_id] = (msg_type, msg_info["NUM_TIMES_RCVD"])
        return rcvd_msgs

    def get_num_ignored_msgs(self):
        return self.num_ignored_msgs

    def get_swarm_snapshot(self, message=None):
        swarm_snapshot = {}

        swarm_snapshot[self.get_id()] = self.get_connections()

        if message is None:
            snapshot_id = randint(1, 1000000)
        else:
            snapshot_id = message.get_message_payload()["SNAPSHOT_ID"]
            for _, msg_info in self.msg_inbox.items():
                if (msg_info["MSG"].get_message_type() == MessageTypes.SWARM_SNAPSHOT) and (msg_info["MSG"].get_message_payload()["SNAPSHOT_ID"] == snapshot_id):
                    return swarm_snapshot
            for _, msg_info in self.sent_messages.items():
                if (msg_info["SENT_MSG"].get_message_type() == MessageTypes.SWARM_SNAPSHOT) and (msg_info["SENT_MSG"].get_message_payload()["SNAPSHOT_ID"] == snapshot_id):
                    return swarm_snapshot

        for bot_id in self.get_connections():
            partial_snapshot = self.create_message(bot_id, MessageTypes.SWARM_SNAPSHOT, {"SNAPSHOT_ID": snapshot_id}, True)[0].get_message_payload()["SHAPSHOT"]
            for bot_id, connections in partial_snapshot.items():
                if bot_id not in swarm_snapshot:
                    swarm_snapshot[bot_id] = []
                for connection in connections:
                    if connection not in swarm_snapshot[bot_id]:
                        swarm_snapshot[bot_id].append(connection)

        return swarm_snapshot

    def add_idle_listener(self, new_listener):
        self.idle_listeners.append(new_listener)

    def is_idle(self):
        return self.num_processes == 0

    def notify_process_state(self, process_running):
        print("Notify process state for bot {}. State: {}".format(self.get_id(), process_running))

        curr_state = self.is_idle()

        if process_running:
            self.num_processes += 1
        else:
            self.num_processes -= 1

        new_state = self.is_idle()

        if curr_state != new_state:
            for listener in self.idle_listeners:
                listener.notify_idle_state(new_state)
