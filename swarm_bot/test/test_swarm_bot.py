import logging
import unittest

from swarm_bot.src.swarm_bot import SwarmBot


class TestSwarmBot(unittest.TestCase):
    def test_swarm_bot_will_throw_error_when_data_flow_is_defined_with_unknown_bots(self):
        test_swarm_bot_1 = SwarmBot()

        sensor_id = 0

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [15])

        self.assertIn("unknown sensor", str(raised_error.exception))

        test_swarm_bot_1.add_sensor(sensor_id)

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [15])

        self.assertIn("unknown swarm bot", str(raised_error.exception))

    def test_swarm_bot_will_follow_defined_data_flow_when_sensor_value_read(self):
        test_swarm_bot_1 = SwarmBot()
        test_swarm_bot_2 = SwarmBot()
        test_swarm_bot_3 = SwarmBot()

        sensor_id = 0
        test_swarm_bot_1.add_sensor(sensor_id)

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_3)

        test_swarm_bot_1.define_data_flow(sensor_id, [test_swarm_bot_1.get_id(), test_swarm_bot_2.get_id(), test_swarm_bot_3.get_id()])

        sensor_read_val = test_swarm_bot_1.read_from_sensor(sensor_id)

        self.assertIn(sensor_read_val, test_swarm_bot_1.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertIn(sensor_read_val, test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertIn(sensor_read_val, test_swarm_bot_3.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
