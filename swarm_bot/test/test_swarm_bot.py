import logging
import unittest

from swarm_bot.test.swarm_bot_test_class import SwarmBotTestClass


class TestSwarmBot(SwarmBotTestClass):
    def test_assert_connecting_to_a_bot_will_form_a_one_way_connection(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)

        self.assertTrue(test_swarm_bot_1.is_connected_to(test_swarm_bot_2.get_id()))
        self.assertFalse(test_swarm_bot_2.is_connected_to(test_swarm_bot_1.get_id()))

    def test_assert_disconnecting_from_a_bot_will_only_delete_the_connection_in_one_direction(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_2.connect_to_swarm_bot(test_swarm_bot_1)

        self.assertTrue(test_swarm_bot_1.is_connected_to(test_swarm_bot_2.get_id()))
        self.assertTrue(test_swarm_bot_2.is_connected_to(test_swarm_bot_1.get_id()))

        test_swarm_bot_1.disconnect_from_swarm_bot(test_swarm_bot_2.get_id())

        self.assertFalse(test_swarm_bot_1.is_connected_to(test_swarm_bot_2.get_id()))
        self.assertTrue(test_swarm_bot_2.is_connected_to(test_swarm_bot_1.get_id()))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
