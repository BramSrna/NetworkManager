import logging
import unittest

from control_centre.src.control_centre import ControlCentre
from swarm_bot.src.swarm_bot import SwarmBot
from http_mock.src.http_mock import HttpMock

class TestE2e(unittest.TestCase):
    def test_data_flows_can_be_assigned_to_sensors(self):
        test_http_mock = HttpMock()
        test_control_centre = ControlCentre(test_http_mock)

        test_swarm_bot = SwarmBot(test_http_mock)
        test_swarm_bot_id = test_swarm_bot.get_id()

        test_control_centre.add_swarm_bot(test_swarm_bot)

        test_sensor_id = "SENSOR_NAME"
        test_swarm_bot.add_sensor(test_sensor_id)

        test_control_centre.define_data_flow(test_swarm_bot_id, test_sensor_id, [test_control_centre.get_id()])

        expected_val = test_swarm_bot.read_from_sensor("SENSOR_NAME")
        actual_val = test_control_centre.read_from_memory(test_swarm_bot_id, test_sensor_id)[0]
        self.assertEqual(expected_val, actual_val)
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()