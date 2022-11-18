import traceback
import logging

from random import randint

import sys

sys.path.append('../..')

from swarm_bot.src.swarm_bot import SwarmBot  # noqa: E402
from swarm_bot.src.swarm_bot_idle_listener_interface import SwarmBotIdleListenerInterface  # noqa: E402
from swarm_bot.src.propagation_strategy.smart_propagation import SmartPropagation  # noqa: E402
from swarm_bot.src.propagation_strategy.naive_propagation import NaivePropagation  # noqa: E402


class PropagationStrategyComparer(SwarmBotIdleListenerInterface):
    def __init__(self, num_bots, connectivity_percentage, num_messages, propagation_strategy):
        SwarmBotIdleListenerInterface.__init__(self)

        self.logger = logging.getLogger('SwarmBot')

        self.num_bots = num_bots
        self.connectivity_percentage = connectivity_percentage
        self.num_messages = num_messages
        self.propagation_strategy = propagation_strategy

        self.swarm_bots = []

    def simulate_prop_strat(self, display_snapshot_info):
        data = None

        try:
            self._initialize_swarm()

            start_snapshot = self._get_state_snapshot()
            self._run_traffic(self.num_messages)
            end_snapshot = self._get_state_snapshot()

            data = self._compare_snapshots(start_snapshot, end_snapshot)
        except Exception as e:
            self.logger.exception(traceback.format_exc())

        for bot in self.swarm_bots:
            bot.teardown()

        if display_snapshot_info:
            self._display_snapshot_info(data)

        return self.swarm_bots, data

    def _display_snapshot_info(self, snapshot):
        for bot_id, bot_info in snapshot.items():
            self.logger.info("BOT_ID: {}".format(bot_id))
            for key in bot_info.keys():
                value = bot_info[key]
                if isinstance(value, dict):
                    self.logger.info("\t{}".format(key))
                    for sub_key, sub_val in value.items():
                        self.logger.info("\t\t{}: {}".format(sub_key, sub_val))
                else:
                    self.logger.info("\t{}: {}".format(key, value))

    def _initialize_swarm(self):
        self.swarm_bots = []

        for _ in range(self.num_bots):
            new_bot = SwarmBot(additional_config_dict={"propagation_strategy": self.propagation_strategy})
            self.swarm_bots.append(new_bot)
            new_bot.add_idle_listener(self)

        for i in range(len(self.swarm_bots)):
            connected = [i]
            num_connections = (self.num_bots - 1) * self.connectivity_percentage / 100.0
            while num_connections > 0:
                rand_bot_ind = i
                while rand_bot_ind in connected:
                    rand_bot_ind = randint(0, self.num_bots - 1)
                self.logger.debug("Connecting {} to {}".format(self.swarm_bots[i].get_id(), self.swarm_bots[rand_bot_ind].get_id()))
                self.swarm_bots[i].connect_to_swarm_bot(self.swarm_bots[rand_bot_ind])
                connected.append(rand_bot_ind)
                num_connections -= 1
        self.wait_for_idle_swarm(60)

    def _run_traffic(self, num_messages):

        bot_ind = 0
        while num_messages > 0:
            bot = self.swarm_bots[bot_ind]
            msg_id = bot.create_propagation_message("TEST", {})
            self.wait_for_idle_swarm(60)
            for bot in self.swarm_bots:
                assert(bot.interacted_with_msg_with_id(msg_id))
            bot_ind += 1
            bot_ind %= len(self.swarm_bots)
            num_messages -= 1

    def _get_state_snapshot(self):
        info_dict = {}
        for bot in self.swarm_bots:
            info_dict[bot.get_id()] = {
                "SENT_MSGS": bot.get_sent_messages(),
                "RCVD_MSGS": bot.get_received_messages(),
                "NUM_IGNORED_MSGS": bot.get_num_ignored_msgs()
            }
        return info_dict

    def _compare_snapshots(self, start_snapshot, end_snapshot):
        data = {}
        for bot_id, bot_info in start_snapshot.items():
            data[bot_id] = {}
            for key in bot_info.keys():
                end_val = end_snapshot[bot_id][key]
                start_val = start_snapshot[bot_id][key]

                if isinstance(end_snapshot[bot_id][key], dict):
                    data[bot_id][key] = {}
                    for msg_id in end_val.keys():
                        if msg_id not in start_val.keys():
                            data[bot_id][key][msg_id] = end_val[msg_id]
                else:
                    data[bot_id][key] = end_val - start_val
        return data


if __name__ == "__main__":
    num_bots = 7
    propagation_strategy = NaivePropagation
    propagation_strategy = SmartPropagation

    comparer = PropagationStrategyComparer(num_bots, 100, 1, propagation_strategy)
    comparer.simulate_prop_strat(True, False)
