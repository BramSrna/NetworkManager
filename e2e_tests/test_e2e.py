import logging
import unittest

from swarm_bot.src.swarm_bot import SwarmBot
from http_mock.src.http_mock import HttpMock
from swarm_manager.src.swarm_manager import SwarmManager
from swarm_manager.src.swarm_connectivity_level import SwarmConnectivityLevel

class TestE2e(unittest.TestCase):
    def test_data_flows_can_be_assigned_to_sensors(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.FULLY_CONNECTED)

        test_swarm_bot_1 = SwarmBot()
        test_swarm_bot_2 = SwarmBot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)

        test_sensor_id = "SENSOR_NAME"
        test_swarm_bot_1.add_sensor(test_sensor_id)

        test_swarm_bot_1.define_data_flow(test_sensor_id, [test_swarm_bot_2.get_id()])

        expected_val = test_swarm_bot_1.read_from_sensor("SENSOR_NAME")
        actual_val = test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), test_sensor_id)[0]
        self.assertEqual(expected_val, actual_val)
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()