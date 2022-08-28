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
    def __init__(self, propagation_strategy=NaivePropagation):
        self.id = id(self)

        self.sensors = {}
        self.memory = {}
        self.data_flows = {}

        self.msg_channels = {}

        self.sent_messages = {}
        self.rcvd_messages = {}

        self.msg_inbox = []
        self.msg_outbox = []

        self.MSG_RESPONSE_TIMEOUT_LIMIT = 10

        self.assigned_task = None
        self.task_queue = []

        self.task_execution_history = []

        self.propagation_strategy = propagation_strategy(self)

        self.run_bot = threading.Event()
        self.msg_inbox_has_values = threading.Event()
        self.msg_outbox_has_values = threading.Event()
        self.task_queue_has_values = threading.Event()

        self.num_ignored_msgs = 0

        self.idle_listeners = []

        self.num_processes = 0

        self.msg_handler_dict = {
            str(MessageTypes.SENSOR_VAL): self.handle_sensor_val_message,
            str(MessageTypes.MSG_RESPONSE): self.handle_msg_response_message,
            str(MessageTypes.NEW_TASK): self.handle_new_task_message,
            str(MessageTypes.REQUEST_TASK_TRANSFER): self.handle_request_task_transfer_message,
            str(MessageTypes.BASIC_PROPAGATION_MESSAGE): self.handle_basic_propagation_message_message,
            str(MessageTypes.SYNC_MESSAGES): self.handle_sync_messages_message
        }

        self.startup()

    def teardown(self):
        self.run_bot.set()
        self.msg_inbox_has_values.set()
        self.msg_outbox_has_values.set()
        self.task_queue_has_values.set()

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
        self.msg_inbox.append(message)
        self.msg_inbox_has_values.set()

    def create_message(self, target_bot_id: int, message_type: MessageTypes, message_payload: dict, message_id=None) -> None:
        targets = []
        if target_bot_id is None:
            targets = self.propagation_strategy.determine_prop_targets(None)
        elif target_bot_id in self.msg_channels:
            targets.append(target_bot_id)
        else:
            raise Exception("ERROR: Tried to create message for unknown bot ID: " + str(target_bot_id))

        if message_id is None:
            message_id = randint(0, 1000000)

        for target in targets:
            new_msg = LocalMessageWrapper(message_id, self.get_id(), target_bot_id, message_type, message_payload)

            self.msg_outbox.append({"MESSAGE": new_msg, "TARGET_ID": target})
            self.msg_outbox_has_values.set()

        return message_id

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
                    self.create_message(id, MessageTypes.SENSOR_VAL, {"SENSOR_ID": sensor_id, "DATA": read_val})

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

    def receive_task(self, new_task):
        self.task_queue.append({"TASK": new_task})
        if len(self.task_queue) > 1:
            self.create_message(None, MessageTypes.NEW_TASK, {"TASK_ID": new_task.get_id(), "TASK_HOLDER": self.get_id()})
        self.task_queue_has_values.set()

    def get_task_queue(self):
        return self.task_queue

    def get_task_execution_history(self):
        return self.task_execution_history

    def startup(self):
        thread = threading.Thread(target=self.task_executor_loop)
        thread.start()
        thread = threading.Thread(target=self.msg_sender_loop)
        thread.start()
        thread = threading.Thread(target=self.msg_receiver_loop)
        thread.start()

    def get_message_channels(self):
        return self.msg_channels

    def send_basic_propagation_message(self):
        return self.create_message(None, MessageTypes.BASIC_PROPAGATION_MESSAGE, {})

    def received_msg_with_id(self, msg_id):
        print(msg_id)
        print(self.rcvd_messages)
        return msg_id in self.rcvd_messages

    def sent_msg_with_id(self, msg_id):
        print(msg_id)
        print(self.rcvd_messages)
        return msg_id in self.sent_messages

    def interacted_with_msg_with_id(self, msg_id):
        return ((msg_id in self.rcvd_messages) or (msg_id in self.sent_messages))

    def sync_with_bot(self, bot_id):
        msg_list = []
        for msg_id, msg_info in self.sent_messages.items():
            if msg_info["SENT_MSG"].get_target_bot_id() is None:
                msg_list.append(msg_id)
        for msg_id, msg_info in self.rcvd_messages.items():
            if msg_info["MSG"].get_target_bot_id() is None:
                msg_list.append(msg_id)

        self.create_message(bot_id, MessageTypes.SYNC_MESSAGES, {"MSG_LIST": msg_list})

    def get_sent_messages(self):
        sent_msgs = {}
        for _, msg_info in self.sent_messages.items():
            msg_id = msg_info["SENT_MSG"].get_id()
            msg_type = msg_info["SENT_MSG"].get_message_type()
            sent_msgs[msg_id] = (msg_type, msg_info["NUM_TIMES_SENT"])
        return sent_msgs

    def get_received_messages(self):
        rcvd_msgs = {}
        for _, msg_info in self.rcvd_messages.items():
            msg_id = msg_info["MSG"].get_id()
            msg_type = msg_info["MSG"].get_message_type()
            rcvd_msgs[msg_id] = (msg_type, msg_info["NUM_TIMES_RCVD"])
        return rcvd_msgs

    def get_num_ignored_msgs(self):
        return self.num_ignored_msgs

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

    def handle_msg_response_message(self, message):
        orig_msg_id = message.get_message_payload()["ORIG_MSG_ID"]
        if (orig_msg_id not in self.sent_messages):
            raise Exception("ERROR: Received message for unsent message: {}".format(orig_msg_id))

        orig_msg_type = self.sent_messages[orig_msg_id]["SENT_MSG"].get_message_type()
        if orig_msg_type == MessageTypes.SYNC_MESSAGES:
            message_payload = message.get_message_payload()
            missing_msg_list = message_payload["MSG_LIST"]

            for msg_id in missing_msg_list:
                curr_msg = None
                if msg_id in self.sent_messages:
                    curr_msg = self.sent_messages[msg_id]["SENT_MSG"]
                else:
                    curr_msg = self.rcvd_messages[msg_id]["MSG"]
                self.create_message(message.get_sender_id(), curr_msg.get_message_type(), curr_msg.get_message_payload(), message_id=msg_id)
        elif orig_msg_type == MessageTypes.REQUEST_TASK_TRANSFER:
            self.receive_task(message.get_message_payload()["TASK"])
        else:
            raise Exception("ERROR: Received message response for unexpected message type: {}".format(orig_msg_type))

    def handle_sensor_val_message(self, message):
        message_payload = message.get_message_payload()
        sender_id = message.get_sender_id()

        sensor_id = message_payload["SENSOR_ID"]
        data = message_payload["DATA"]

        self.write_to_memory(sender_id, sensor_id, data)

    def handle_new_task_message(self, message):
        message_payload = message.get_message_payload()

        self.task_queue.append({"HOLDER_ID": message_payload["TASK_HOLDER"], "TASK_ID": message_payload["TASK_ID"]})

        self.task_queue_has_values.set()

    def handle_request_task_transfer_message(self, message):
        message_payload = message.get_message_payload()
        msg_id = message.get_id()

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
            if len(self.task_queue) == 0:
                self.task_queue_has_values.clear()
        self.create_message(message.get_sender_id(), MessageTypes.MSG_RESPONSE, {"ORIG_MSG_ID": msg_id, "TASK": task})

    def handle_basic_propagation_message_message(self, message):
        pass

    def handle_sync_messages_message(self, message):
        message_payload = message.get_message_payload()
        msg_id = message.get_id()

        id_list = message_payload["MSG_LIST"]
        missing_msgs = []

        rcvd_msg_ids = list(self.rcvd_messages.keys())
        sent_msg_ids = list(self.sent_messages.keys())

        for curr_msg_id in id_list:
            if (curr_msg_id not in rcvd_msg_ids) and (curr_msg_id not in sent_msg_ids):
                missing_msgs.append(curr_msg_id)

        self.create_message(message.get_sender_id(), MessageTypes.MSG_RESPONSE, {"ORIG_MSG_ID": msg_id, "MSG_LIST": missing_msgs})

    def task_executor_loop(self):
        while (not self.run_bot.is_set()):
            self.task_queue_has_values.wait()
            while (len(self.task_queue) > 0) and (not self.run_bot.is_set()):
                self.notify_process_state(True)
                next_task = None
                while (next_task is None) and len(self.task_queue) > 0:
                    next_task_info = self.task_queue.pop(0)
                    if "TASK" in next_task_info:
                        next_task = next_task_info["TASK"]
                    else:
                        self.create_message(next_task_info["HOLDER_ID"], MessageTypes.REQUEST_TASK_TRANSFER, {"TASK_ID": next_task_info["TASK_ID"]})
                if next_task is not None:
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

            if len(self.task_queue) == 0:
                self.task_queue_has_values.clear()

    def msg_sender_loop(self):
        while (not self.run_bot.is_set()):
            self.msg_outbox_has_values.wait()
            while (len(self.msg_outbox) > 0) and (not self.run_bot.is_set()):
                self.notify_process_state(True)
                msg_to_send = self.msg_outbox.pop(0)

                message = msg_to_send["MESSAGE"]

                targets = [msg_to_send["TARGET_ID"]]
                if targets is None:
                    targets = list(self.msg_channels.keys())

                for target_bot_id in targets:
                    if target_bot_id not in self.msg_channels:
                        raise Exception("ERROR: Tried to send message to unknown bot ID: {}. Known bot list: {}".format(str(target_bot_id), self.msg_channels.keys()))

                if len(targets) == 0:
                    raise Exception("ERROR: Tried to send message with no targets: {}".format(str(message)))

                msg_id = message.get_id()

                if msg_id not in self.sent_messages:
                    self.sent_messages[msg_id] = {"TIME_SENT": time.time(), "SENT_MSG": message, "NUM_TIMES_SENT": 0}

                self.sent_messages[msg_id]["NUM_TIMES_SENT"] += 1

                for bot_id in targets:
                    print("Sent message. Sender bot ID: {}, target bot ID: {}, message ID {}, message type: {}, sender message list {}\n\n".format(self.get_id(), target_bot_id, msg_id, message.get_message_type(), self.sent_messages))
                    self.msg_channels[bot_id].send_message(message)

                self.notify_process_state(False)

            if len(self.msg_inbox) == 0:
                self.msg_outbox_has_values.clear()

    def msg_receiver_loop(self):
        while not self.run_bot.is_set():
            self.msg_inbox_has_values.wait()
            while (len(self.msg_inbox) > 0) and (not self.run_bot.is_set()):
                self.notify_process_state(True)

                message = self.msg_inbox.pop(0)

                target_id = message.get_target_bot_id()
                msg_id = message.get_id()
                message_type = str(message.get_message_type())
                message_payload = message.get_message_payload()

                print("Received message. receiver bot ID: {}, target bot ID: {}, message ID {}, message type {}, payload: {}\n\n".format(self.get_id(), target_id, msg_id, message_type, message_payload))

                sender_id = message.get_sender_id()
                if (sender_id is not None) and (sender_id != self.get_id()) and (sender_id not in self.msg_channels):
                    raise Exception("ERROR: Received message from unknown bot: {}. Known bot list: {}".format(str(sender_id), self.msg_channels.keys()))

                if (self.interacted_with_msg_with_id(msg_id)):
                    if msg_id not in self.rcvd_messages:
                        self.rcvd_messages[msg_id] = {"MSG": message, "NUM_TIMES_RCVD": 0}
                    self.rcvd_messages[msg_id]["NUM_TIMES_RCVD"] += 1
                    self.num_ignored_msgs += 1
                    if target_id is None:
                        self.propagation_strategy.track_message_propagation(message)
                else:
                    self.rcvd_messages[msg_id] = {"MSG": message, "NUM_TIMES_RCVD": 1}

                    if message_type in self.msg_handler_dict:
                        self.msg_handler_dict[message_type](message)
                    else:
                        raise Exception("ERROR: Unknown message type: " + str(message_type))

                    if target_id is None:
                        targets = self.propagation_strategy.determine_prop_targets(message)
                        for target_bot_id in targets:
                            self.create_message(target_bot_id, message_type, message_payload, message_id=msg_id)

                    if (len(self.rcvd_messages.keys()) > 0) and (len(self.rcvd_messages.keys()) % 10 == 0):
                        bot_ids = list(self.msg_channels.keys())
                        for bot_id in bot_ids:
                            self.sync_with_bot(bot_id)

                self.notify_process_state(False)

            if len(self.msg_inbox) == 0:
                self.msg_inbox_has_values.clear()
