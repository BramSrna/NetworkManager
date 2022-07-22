import logging
import unittest
import time

from swarm_bot.test.swarm_bot_test_class import SwarmBotTestClass
from swarm_bot.src.swarm_bot_sensor import SwarmBotSensor


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

        start_time = time.time()
        while ((time.time() < start_time + 10) and not (test_swarm_bot_2.received_msg_with_id(msg_id) and test_swarm_bot_3.received_msg_with_id(msg_id))):
            pass

        self.assertFalse(test_swarm_bot_1.received_msg_with_id(msg_id))

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

        start_time = time.time()
        while ((time.time() < start_time + 10) and not (test_swarm_bot_4.received_msg_with_id(msg_id) and test_swarm_bot_5.received_msg_with_id(msg_id) and test_swarm_bot_6.received_msg_with_id(msg_id) and test_swarm_bot_7.received_msg_with_id(msg_id))):
            pass

        self.assertFalse(test_swarm_bot_1.received_msg_with_id(msg_id))

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

        start_time = time.time()
        while ((time.time() < start_time + 10) and not (test_swarm_bot_2.received_msg_with_id(msg_id) and test_swarm_bot_3.received_msg_with_id(msg_id) and test_swarm_bot_4.received_msg_with_id(msg_id) and test_swarm_bot_5.received_msg_with_id(msg_id))):
            pass

        self.assertFalse(test_swarm_bot_1.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_2.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_3.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_4.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_5.received_msg_with_id(msg_id))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
