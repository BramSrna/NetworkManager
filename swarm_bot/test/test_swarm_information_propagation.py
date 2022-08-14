import logging
import unittest

from swarm_bot.test.swarm_bot_test_class import SwarmBotTestClass
from swarm_bot.src.swarm_bot_sensor import SwarmBotSensor
from swarm_bot.test.propagation_strategy_comparer import PropagationStrategyComparer


class SimpleSensor(SwarmBotSensor):
    def __init__(self):
        super().__init__()

    def read_from_sensor(self, additional_params):
        return True


class TestSwarmInformationPropagation(SwarmBotTestClass):
    def test_all_bots_in_the_swarm_receive_a_sent_message_when_naive_propagation_is_used_in_double_layer_network(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_3)

        msg_id = test_swarm_bot_1.send_basic_propagation_message()

        self.wait_for_idle_swarm()

        self.assertTrue(test_swarm_bot_2.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_3.received_msg_with_id(msg_id))

    def test_all_bots_in_the_swarm_receive_a_sent_message_when_naive_propagation_is_used_in_multi_layer_network(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()
        test_swarm_bot_4 = self.create_swarm_bot()
        test_swarm_bot_5 = self.create_swarm_bot()
        test_swarm_bot_6 = self.create_swarm_bot()
        test_swarm_bot_7 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_3)

        test_swarm_bot_2.connect_to_swarm_bot(test_swarm_bot_4)
        test_swarm_bot_2.connect_to_swarm_bot(test_swarm_bot_5)

        test_swarm_bot_3.connect_to_swarm_bot(test_swarm_bot_6)
        test_swarm_bot_3.connect_to_swarm_bot(test_swarm_bot_7)

        msg_id = test_swarm_bot_1.send_basic_propagation_message()

        self.wait_for_idle_swarm()

        self.assertTrue(test_swarm_bot_2.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_3.received_msg_with_id(msg_id))

        self.assertTrue(test_swarm_bot_4.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_5.received_msg_with_id(msg_id))

        self.assertTrue(test_swarm_bot_6.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_7.received_msg_with_id(msg_id))

    def test_all_bots_in_the_swarm_receive_a_sent_message_when_naive_propagation_is_used_in_circular_network(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()
        test_swarm_bot_4 = self.create_swarm_bot()
        test_swarm_bot_5 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_2.connect_to_swarm_bot(test_swarm_bot_3)
        test_swarm_bot_3.connect_to_swarm_bot(test_swarm_bot_4)
        test_swarm_bot_4.connect_to_swarm_bot(test_swarm_bot_5)
        test_swarm_bot_5.connect_to_swarm_bot(test_swarm_bot_1)

        msg_id = test_swarm_bot_1.send_basic_propagation_message()

        self.wait_for_idle_swarm()

        self.assertTrue(test_swarm_bot_2.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_3.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_4.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_5.received_msg_with_id(msg_id))

    def test_naive_propagation_is_better_than_worst_case_implementation(self):
        num_bots = 3
        connectivity_percentage = 100
        num_messages = 1

        comparer = PropagationStrategyComparer(num_bots, connectivity_percentage, num_messages)
        bots, test_output = comparer.simulate_prop_strat(False, False)

        self.assertEqual(num_bots, len(test_output.keys()))

        ignoring_n_minus_one = 0
        ignoring_n_minus_two = 0
        ignoring_else = 0

        for _, bot_info in test_output.items():
            total_sent_msgs = 0
            total_rcvd_msgs = 0

            for _, msg_info in bot_info["SENT_MSGS"].items():
                total_sent_msgs += msg_info[1]
            for _, msg_info in bot_info["RCVD_MSGS"].items():
                total_rcvd_msgs += msg_info[1]

            self.assertEqual(num_bots - 1, total_sent_msgs)
            self.assertEqual(num_bots - 1, total_rcvd_msgs)

            num_ignored = bot_info["NUM_IGNORED_MSGS"]
            if num_ignored == num_bots - 1:
                ignoring_n_minus_one += 1
            elif num_ignored == num_bots - 2:
                ignoring_n_minus_two += 1
            else:
                ignoring_else += 1

        # Only the source bot should ignore n - 1 messages
        self.assertEqual(1, ignoring_n_minus_one)

        # All receiver bots should ignore n - 2 messages
        self.assertEqual(num_bots - 1, ignoring_n_minus_two)

        self.assertEqual(0, ignoring_else)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
