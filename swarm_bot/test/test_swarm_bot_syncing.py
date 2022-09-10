import logging
import unittest
from unittest.mock import MagicMock

from swarm_bot_test_class import SwarmBotTestClass
from swarm_bot.src.swarm_bot_sensor import SwarmBotSensor


class SimpleSensor(SwarmBotSensor):
    def __init__(self):
        super().__init__()

    def read_from_sensor(self, additional_params):
        return True


class TestSwarmInformationPropagation(SwarmBotTestClass):
    def test_swarm_bot_will_send_previously_propagated_messages_to_a_newly_connected_bot(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)

        msg_id = test_swarm_bot_1.send_basic_propagation_message()

        self.wait_for_idle_swarm()

        self.assertTrue(test_swarm_bot_2.received_msg_with_id(msg_id))
        self.assertFalse(test_swarm_bot_3.received_msg_with_id(msg_id))

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_3)

        self.wait_for_idle_swarm()

        self.assertTrue(test_swarm_bot_2.received_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_3.received_msg_with_id(msg_id))

    def test_swarm_bot_will_resync_every_tenth_message_received(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_3)

        test_swarm_bot_2.sync_with_bot = MagicMock()
        test_swarm_bot_3.sync_with_bot = MagicMock()

        for _ in range(10):
            test_swarm_bot_1.send_basic_propagation_message()
            self.wait_for_idle_swarm()

        test_swarm_bot_2.sync_with_bot.assert_called_with(test_swarm_bot_1.get_id())
        test_swarm_bot_3.sync_with_bot.assert_called_with(test_swarm_bot_1.get_id())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
