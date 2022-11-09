import threading
import time
import os
import yaml

from random import randint
from swarm_bot.src.message_channel.local_message_channel import LocalMessageChannel

from swarm_bot.src.message_types import MessageTypes
from swarm_bot.src.message_channel.message_channel_user import MessageChannelUser

from swarm_bot.src.message_wrapper.local_message_wrapper import LocalMessageWrapper
from swarm_bot.src.message_wrapper.message_wrapper import MessageWrapper
from swarm_bot.src.propagation_strategy.naive_propagation import NaivePropagation
from swarm_bot.src.propagation_strategy.smart_propagation import SmartPropagation


class SwarmBot(MessageChannelUser):
    def __init__(self, additional_config_path=None, additional_config_dict=None):
        self.id = id(self)

        self.msg_channels = {}

        self.sent_messages = {}
        self.rcvd_messages = {}

        self.msg_inbox = []
        self.msg_outbox = []

        self.run_bot = threading.Event()
        self.msg_inbox_has_values = threading.Event()
        self.msg_outbox_has_values = threading.Event()

        self.num_ignored_msgs = 0

        self.idle_listeners = []

        self.num_processes = 0

        self.msg_handler_dict = {}
        self.msg_response_handler_dict = {}
        self.assign_msg_handler(str(MessageTypes.MSG_RESPONSE), self.handle_msg_response_message)

        config = yaml.load(open(os.path.join(os.path.dirname(__file__), "./default_bot_config.yml")), Loader=yaml.FullLoader)
        additional_config = {}
        if additional_config_path is not None:
            additional_config = yaml.load(open(os.path.join(os.path.dirname(__file__), additional_config_path)), Loader=yaml.FullLoader)

        for key, value in additional_config.items():
            config[key] = value

        if additional_config_dict is not None:
            for key, value in additional_config_dict.items():
                config[key] = value

        propagation_strategies = {
            "NaivePropagation": NaivePropagation,
            "SmartPropagation": SmartPropagation
        }

        message_channels = {
            "LocalMessageChannel": LocalMessageChannel
        }

        message_wrappers = {
            "LocalMessageWrapper": LocalMessageWrapper
        }

        self.propagation_strategy = propagation_strategies[config["propagation_strategy"]](self)
        self.message_channel_type = message_channels[config["message_channel"]]
        self.message_wrapper_type = message_wrappers[config["message_wrapper"]]

        self.startup()

    def teardown(self):
        self.run_bot.set()
        self.msg_inbox_has_values.set()
        self.msg_outbox_has_values.set()

    def assign_msg_handler(self, msg_type, handler):
        self.msg_handler_dict[msg_type] = handler

    def assign_msg_response_handler(self, orig_msg_type, handler):
        self.msg_response_handler_dict[orig_msg_type] = handler

    def get_id(self) -> int:
        return self.id

    def connect_to_swarm_bot(self, new_swarm_bot: "SwarmBot") -> None:
        bot_id = new_swarm_bot.get_id()
        if bot_id not in self.msg_channels:
            self.msg_channels[bot_id] = self.message_channel_type(self, new_swarm_bot)
            new_swarm_bot.connect_to_swarm_bot(self)

    def is_connected_to(self, swarm_bot_id: str) -> bool:
        return swarm_bot_id in self.msg_channels

    def get_connections(self) -> list:
        return list(self.msg_channels.keys())

    def receive_message(self, message: MessageWrapper) -> None:
        self.msg_inbox.append(message)
        self.msg_inbox_has_values.set()

    def create_propagation_message(self, message_type: MessageTypes, message_payload: dict, message_id=None, msg_ref=None) -> None:
        targets = self.propagation_strategy.determine_prop_targets(msg_ref)

        # TODO: Improve message ID generation. Ensure duplicate IDs cannot be generated.
        if message_id is None:
            message_id = randint(0, 1000000)

        for target in targets:
            new_msg = self.message_wrapper_type(message_id, self.get_id(), target, message_type, message_payload, True)

            self.msg_outbox.append({"MESSAGE": new_msg, "TARGET_ID": target})
            self.msg_outbox_has_values.set()

        return message_id

    def create_directed_message(self, target_bot_id: int, message_type: MessageTypes, message_payload: dict, message_id=None) -> None:
        if target_bot_id not in self.msg_channels:
            raise Exception("ERROR: Tried to create message for unknown bot ID: " + str(target_bot_id))

        # TODO: Improve message ID generation. Ensure duplicate IDs cannot be generated.
        if message_id is None:
            message_id = randint(0, 1000000)

        new_msg = self.message_wrapper_type(message_id, self.get_id(), target_bot_id, message_type, message_payload, False)

        self.msg_outbox.append({"MESSAGE": new_msg, "TARGET_ID": target_bot_id})
        self.msg_outbox_has_values.set()

        return message_id

    def startup(self):
        thread = threading.Thread(target=self.msg_sender_loop)
        thread.start()
        thread = threading.Thread(target=self.msg_receiver_loop)
        thread.start()

    def get_message_channels(self):
        return self.msg_channels

    def received_msg_with_id(self, msg_id):
        return msg_id in self.rcvd_messages

    def sent_msg_with_id(self, msg_id):
        return msg_id in self.sent_messages

    def interacted_with_msg_with_id(self, msg_id):
        return ((msg_id in self.rcvd_messages) or (msg_id in self.sent_messages))

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
        self.msg_response_handler_dict[orig_msg_type](message)

    def msg_sender_loop(self):
        while (not self.run_bot.is_set()):
            self.msg_outbox_has_values.wait()
            while (len(self.msg_outbox) > 0) and (not self.run_bot.is_set()):
                self.notify_process_state(True)
                msg_to_send = self.msg_outbox.pop(0)

                message = msg_to_send["MESSAGE"]

                targets = [msg_to_send["TARGET_ID"]]

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
                should_propagate = message.get_propagation_flag()

                print("Received message. receiver bot ID: {}, target bot ID: {}, message ID {}, message type {}, payload: {}\n\n".format(self.get_id(), target_id, msg_id, message_type, message_payload))

                sender_id = message.get_sender_id()
                if (sender_id is not None) and (sender_id != self.get_id()) and (sender_id not in self.msg_channels):
                    raise Exception("ERROR: Received message from unknown bot: {}. Known bot list: {}".format(str(sender_id), self.msg_channels.keys()))

                if (self.interacted_with_msg_with_id(msg_id)):
                    if msg_id not in self.rcvd_messages:
                        self.rcvd_messages[msg_id] = {"MSG": message, "NUM_TIMES_RCVD": 0}
                    self.rcvd_messages[msg_id]["NUM_TIMES_RCVD"] += 1
                    self.num_ignored_msgs += 1
                    if should_propagate:
                        self.propagation_strategy.track_message_propagation(message)
                else:
                    self.rcvd_messages[msg_id] = {"MSG": message, "NUM_TIMES_RCVD": 1}

                    if message_type in self.msg_handler_dict:
                        self.msg_handler_dict[message_type](message)
                    else:
                        print("Warning: Received message type with no assigned handler: " + str(message_type))

                    if should_propagate:
                        self.create_propagation_message(message_type, message_payload, message_id=msg_id, msg_ref=message)

                self.notify_process_state(False)

            if len(self.msg_inbox) == 0:
                self.msg_inbox_has_values.clear()
