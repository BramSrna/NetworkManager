import sys
import time

from swarm_bot.src.propagation_strategy.propagation_strategy import PropagationStrategy


class SmartPropagation(PropagationStrategy):
    def __init__(self, owner_swarm_bot):
        super().__init__(owner_swarm_bot)

        self.message_tracker = {}
        self.avg_receive_time_tracker = {}

        for bot_id in self.swarm_bot.get_message_channels().keys():
            self.add_bot_to_tracker_if_not_present(bot_id)

    def add_bot_to_tracker_if_not_present(self, bot_id):
        if bot_id not in self.avg_receive_time_tracker:
            self.avg_receive_time_tracker[bot_id] = {
                "NUM_RCVD_MSGS": 0,
                "CURR_AVG": sys.maxsize
            }

    def determine_prop_targets(self, message):
        targets = []
        for bot_id in self.swarm_bot.get_message_channels().keys():
            if (message is None) or (bot_id != message.get_sender_id()):
                targets.append(bot_id)
            self.add_bot_to_tracker_if_not_present(bot_id)

        sorted_targets = sorted(targets, key=lambda bot_id: self.avg_receive_time_tracker[bot_id]["CURR_AVG"], reverse=True)
        print("SORTED TARGETS: {}".format(str(sorted_targets)))
        return sorted_targets

    def track_message_propagation(self, message):
        message_id = message.get_id()
        time_received = time.time()

        if message not in self.message_tracker:
            self.message_tracker[message_id] = time_received

        time_receive_diff = time_received - self.message_tracker[message_id]

        sender_id = message.get_sender_id()

        self.add_bot_to_tracker_if_not_present(sender_id)

        curr_percent = self.avg_receive_time_tracker[sender_id]["NUM_RCVD_MSGS"] / 100
        new_avg = (self.avg_receive_time_tracker[sender_id]["CURR_AVG"] * curr_percent) + (time_receive_diff * (1 - curr_percent))
        self.avg_receive_time_tracker[sender_id]["CURR_AVG"] = new_avg
        self.avg_receive_time_tracker[sender_id]["NUM_RCVD_MSGS"] += 1
