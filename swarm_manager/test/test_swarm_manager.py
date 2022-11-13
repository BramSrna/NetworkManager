import logging
import unittest

from swarm_bot.src.swarm_bot import SwarmBot
from swarm_manager.src.swarm_manager import SwarmManager
from swarm_manager.src.swarm_connectivity_level import SwarmConnectivityLevel


class TestSwarmManager(unittest.TestCase):
    def setUp(self):
        self.test_swarm_bots = []
        self.test_swarm_managers = []

    def tearDown(self):
        for bot in self.test_swarm_bots:
            bot.teardown()

    def create_swarm_bot(self):
        new_bot = SwarmBot()
        self.test_swarm_bots.append(new_bot)
        return new_bot

    def create_swarm_manager(self, connectivity_type):
        new_manager = SwarmManager(connectivity_type)
        self.test_swarm_managers.append(new_manager)
        return new_manager

    def test_new_bot_added_in_fully_connected_network_will_be_connected_to_all_other_bots(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.FULLY_CONNECTED)

        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_3)

        new_swarm_bot = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(new_swarm_bot)

        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_1.get_id()))
        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_2.get_id()))
        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_3.get_id()))

        self.assertTrue(test_swarm_bot_1.is_connected_to(new_swarm_bot.get_id()))
        self.assertTrue(test_swarm_bot_2.is_connected_to(new_swarm_bot.get_id()))
        self.assertTrue(test_swarm_bot_3.is_connected_to(new_swarm_bot.get_id()))

    def test_new_bot_added_in_partially_connected_network_will_be_connected_to_random_bot(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.PARTIALLY_CONNECTED)

        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_3)

        new_swarm_bot = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(new_swarm_bot)

        connections = new_swarm_bot.get_connections()

        self.assertEqual(1, len(connections))
        self.assertIn(connections[0], [test_swarm_bot_1.get_id(), test_swarm_bot_2.get_id(), test_swarm_bot_3.get_id()])

    def test_new_bot_added_in_centralized_network_will_be_connected_to_central_swarm_bot(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.CENTRALIZED)

        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_3)

        new_swarm_bot = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(new_swarm_bot)

        connections = new_swarm_bot.get_connections()

        self.assertEqual(1, len(connections))
        self.assertEqual(test_swarm_manager.get_central_swarm_bot().get_id(), connections[0])

        self.assertTrue(test_swarm_manager.get_central_swarm_bot().is_connected_to(new_swarm_bot.get_id()))

    def test_removing_bot_from_swarm_will_disconnect_it_from_all_bots(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.FULLY_CONNECTED)

        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_3)

        new_swarm_bot = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(new_swarm_bot)

        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_1.get_id()))
        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_2.get_id()))
        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_3.get_id()))

        self.assertTrue(test_swarm_bot_1.is_connected_to(new_swarm_bot.get_id()))
        self.assertTrue(test_swarm_bot_2.is_connected_to(new_swarm_bot.get_id()))
        self.assertTrue(test_swarm_bot_3.is_connected_to(new_swarm_bot.get_id()))

        test_swarm_manager.remove_swarm_bot(new_swarm_bot.get_id())

        self.assertFalse(new_swarm_bot.is_connected_to(test_swarm_bot_1.get_id()))
        self.assertFalse(new_swarm_bot.is_connected_to(test_swarm_bot_2.get_id()))
        self.assertFalse(new_swarm_bot.is_connected_to(test_swarm_bot_3.get_id()))

        self.assertFalse(test_swarm_bot_1.is_connected_to(new_swarm_bot.get_id()))
        self.assertFalse(test_swarm_bot_2.is_connected_to(new_swarm_bot.get_id()))
        self.assertFalse(test_swarm_bot_3.is_connected_to(new_swarm_bot.get_id()))

    def test_swarm_manager_will_throw_an_error_if_removing_a_bot_will_leave_orphan_bots(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.CENTRALIZED)

        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_3)

        new_swarm_bot = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(new_swarm_bot)

        with self.assertRaises(Exception) as raised_error:
            test_swarm_manager.remove_swarm_bot(test_swarm_manager.get_central_swarm_bot().get_id())

        self.assertIn("Removing bot from swarm would leave an orphaned bot", str(raised_error.exception))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
