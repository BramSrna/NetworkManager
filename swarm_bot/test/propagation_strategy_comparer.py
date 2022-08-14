import time
import traceback

from random import randint

import sys

sys.path.append('../..')

from swarm_bot.src.swarm_bot import SwarmBot
from visualizer.src.visualizer import Visualizer
from swarm_bot.src.swarm_bot_idle_listener_interface import SwarmBotIdleListenerInterface

class PropagationStrategyComparer(SwarmBotIdleListenerInterface):
    def __init__(self, num_bots, connectivity_percentage, num_messages):
        SwarmBotIdleListenerInterface.__init__(self)
        
        self.num_bots = num_bots
        self.connectivity_percentage = connectivity_percentage
        self.num_messages = num_messages

        self.swarm_bots = []

    def simulate_prop_strat(self, display_snapshot_info, visualize_swarm):
        data = None

        try:
            self._initialize_swarm()

            start_snapshot = self._get_state_snapshot()
            self._run_traffic(self.num_messages)
            end_snapshot = self._get_state_snapshot()

            data = self._compare_snapshots(start_snapshot, end_snapshot)
        except Exception as e:
            print(repr(e))
            print(traceback.format_exc())

        for bot in self.swarm_bots:
            bot.teardown()

        if display_snapshot_info:
            self._display_snapshot_info(data)

        if visualize_swarm:
            self._visualize_swarm()
            
        return self.swarm_bots, data

    def _display_snapshot_info(self, snapshot):
        for bot_id, bot_info in snapshot.items():
            print("BOT_ID: {}".format(bot_id))
            for key in bot_info.keys():
                value = bot_info[key]
                if isinstance(value, dict):
                    print("\t{}".format(key))
                    for sub_key, sub_val in value.items():
                        print("\t\t{}: {}".format(sub_key, sub_val))
                else:
                    print("\t{}: {}".format(key, value))

    def _visualize_swarm(self):
        visualizer = Visualizer(self.swarm_bots[0])
        visualizer.visualize_swarm()

    def _initialize_swarm(self):
        self.swarm_bots = []

        for _ in range(self.num_bots):
            new_bot = SwarmBot()
            self.swarm_bots.append(new_bot)
            new_bot.add_idle_listener(self)

        for i in range(len(self.swarm_bots)):
            connected = [i]
            num_connections = (self.num_bots - 1) * self.connectivity_percentage / 100.0
            while num_connections > 0:
                rand_bot_ind = i
                while rand_bot_ind in connected:
                    rand_bot_ind = randint(0, self.num_bots - 1)
                print("Connecting {} to {}".format(self.swarm_bots[i].get_id(), self.swarm_bots[rand_bot_ind].get_id()))
                self.swarm_bots[i].connect_to_swarm_bot(self.swarm_bots[rand_bot_ind])
                connected.append(rand_bot_ind)
                num_connections -= 1

    def _run_traffic(self, num_messages):
        bot_ind = 0
        while num_messages > 0:
            bot = self.swarm_bots[bot_ind]
            msg_id = bot.send_basic_propagation_message()
            self.wait_for_idle_swarm()
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
    num_bots = 3

    comparer = PropagationStrategyComparer(num_bots, 100, 1)
    comparer.simulate_prop_strat(True, False)

    # Basic Implementation (Full Connectivity, N = number of bots in the swarm)
    # Every bot:
    #   - Sends N - 1 messages
    #   - Receives N - 1 messages
    #   - Source bot ignores N - 1 messages, Receiver bots ignore N - 2 messages

    # Source bot: Send 2, receive 0, ignore 0
    # Receiver bots: Send 1, receive 2, ignore 1

# BOT_ID: 2915207183856
#         SENT_MSGS
#                 588148: (<MessageTypes.BASIC_PROPAGATION_MESSAGE: 7>, 2)
#         RCVD_MSGS
#                 588148: (<MessageTypes.BASIC_PROPAGATION_MESSAGE: 7>, 2)
#         NUM_IGNORED_MSGS: 2
# BOT_ID: 2915211518656
#         SENT_MSGS
#                 588148: (<MessageTypes.BASIC_PROPAGATION_MESSAGE: 7>, 2)
#         RCVD_MSGS
#                 588148: (<MessageTypes.BASIC_PROPAGATION_MESSAGE: 7>, 2)
#         NUM_IGNORED_MSGS: 1
# BOT_ID: 2915211517792
#         SENT_MSGS
#                 588148: (<MessageTypes.BASIC_PROPAGATION_MESSAGE: 7>, 2)
#         RCVD_MSGS
#                 588148: (<MessageTypes.BASIC_PROPAGATION_MESSAGE: 7>, 2)
#         NUM_IGNORED_MSGS: 1
