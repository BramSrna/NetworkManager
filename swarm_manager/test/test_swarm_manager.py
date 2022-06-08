import logging
import unittest

from swarm_bot.src.swarm_bot import SwarmBot
from swarm_manager.src.swarm_manager import SwarmManager
from swarm_manager.src.swarm_connectivity_level import SwarmConnectivityLevel

class TestSwarmManager(unittest.TestCase):
    def test_new_bot_added_in_fully_connected_network_will_be_connected_to_all_other_bots(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.FULLY_CONNECTED)

        test_swarm_bot_1 = SwarmBot()
        test_swarm_bot_2 = SwarmBot()
        test_swarm_bot_3 = SwarmBot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_3)

        new_swarm_bot = SwarmBot()

        test_swarm_manager.add_swarm_bot(new_swarm_bot)

        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_1.get_id()))
        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_2.get_id()))
        self.assertTrue(new_swarm_bot.is_connected_to(test_swarm_bot_3.get_id()))

    def test_new_bot_added_in_partially_connected_network_will_be_connected_to_random_bot(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.PARTIALLY_CONNECTED)

        test_swarm_bot_1 = SwarmBot()
        test_swarm_bot_2 = SwarmBot()
        test_swarm_bot_3 = SwarmBot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_3)

        new_swarm_bot = SwarmBot()

        test_swarm_manager.add_swarm_bot(new_swarm_bot)

        connections = new_swarm_bot.get_connections()

        self.assertEqual(1, len(connections))
        self.assertIn(connections[0], [test_swarm_bot_1.get_id(), test_swarm_bot_2.get_id(), test_swarm_bot_3.get_id()])

    def test_new_bot_added_in_centralized_network_will_be_connected_to_central_swarm_bot(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.CENTRALIZED)

        test_swarm_bot_1 = SwarmBot()
        test_swarm_bot_2 = SwarmBot()
        test_swarm_bot_3 = SwarmBot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_3)

        new_swarm_bot = SwarmBot()

        test_swarm_manager.add_swarm_bot(new_swarm_bot)

        connections = new_swarm_bot.get_connections()

        self.assertEqual(1, len(connections))
        self.assertEqual(test_swarm_manager.get_central_swarm_bot().get_id(), connections[0])


        

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()