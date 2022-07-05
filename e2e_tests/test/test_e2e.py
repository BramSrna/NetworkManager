import logging
import unittest
import time

from swarm_bot.src.swarm_bot import SwarmBot
from swarm_manager.src.swarm_manager import SwarmManager
from swarm_manager.src.swarm_connectivity_level import SwarmConnectivityLevel
from swarm_bot.src.swarm_bot_sensor import SwarmBotSensor


class SimpleSensor(SwarmBotSensor):
    def __init__(self):
        super().__init__()

    def read_from_sensor(self, additional_params):
        return True


class TestE2e(unittest.TestCase):
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

    def test_data_flows_can_be_assigned_to_sensors(self):
        test_swarm_manager = SwarmManager(SwarmConnectivityLevel.FULLY_CONNECTED)

        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()

        test_swarm_manager.add_swarm_bot(test_swarm_bot_1)
        test_swarm_manager.add_swarm_bot(test_swarm_bot_2)

        test_sensor = SimpleSensor()
        test_sensor_id = test_sensor.get_id()
        test_swarm_bot_1.add_sensor(test_sensor)

        test_swarm_bot_1.define_data_flow(test_sensor_id, [test_swarm_bot_2.get_id()])

        expected_val = test_swarm_bot_1.read_from_sensor(test_sensor_id, ())

        start_time = time.time()
        while ((time.time() < start_time + 10) and (expected_val not in test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), test_sensor_id))):
            pass

        actual_val = test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), test_sensor_id)[0]
        self.assertEqual(expected_val, actual_val)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
