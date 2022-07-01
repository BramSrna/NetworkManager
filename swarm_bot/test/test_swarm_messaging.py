import logging
import unittest
import time

from swarm_bot.src.swarm_bot import SwarmBot
from swarm_bot.test.swarm_bot_test_class import SwarmBotTestClass


class TestSwarmMessaging(SwarmBotTestClass):
    def test_swarm_bot_will_throw_error_when_data_flow_is_defined_with_unreachable_bot_no_bots(self):
        test_swarm_bot_1 = self.create_swarm_bot()

        sensor_id = 0

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [15])

        self.assertIn("unknown sensor", str(raised_error.exception))

        test_swarm_bot_1.add_sensor(sensor_id)

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [15])

        self.assertIn("unreachable swarm bot", str(raised_error.exception))

    def test_swarm_bot_will_throw_error_when_data_flow_is_defined_with_unreachable_bot_through_intermediary(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)

        sensor_id = 0

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [-15])

        self.assertIn("unknown sensor", str(raised_error.exception))

        test_swarm_bot_1.add_sensor(sensor_id)

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [-15])

        self.assertIn("unreachable swarm bot", str(raised_error.exception))

    def test_swarm_bot_will_follow_defined_data_flow_when_sensor_value_read(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        sensor_id = 0
        test_swarm_bot_1.add_sensor(sensor_id)

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_3)

        test_swarm_bot_1.define_data_flow(sensor_id, [test_swarm_bot_1.get_id(), test_swarm_bot_2.get_id(), test_swarm_bot_3.get_id()])

        sensor_read_val = test_swarm_bot_1.read_from_sensor(sensor_id)

        start_time = time.time()
        while ((time.time() < start_time + 10) and (sensor_read_val not in test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))):
            pass

        start_time = time.time()
        while ((time.time() < start_time + 10) and (sensor_read_val not in test_swarm_bot_3.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))):
            pass

        self.assertIn(sensor_read_val, test_swarm_bot_1.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertIn(sensor_read_val, test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertIn(sensor_read_val, test_swarm_bot_3.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))

    def test_messages_can_propagate_through_intermediary_bots(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        sensor_id = 0
        test_swarm_bot_1.add_sensor(sensor_id)

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_2.connect_to_swarm_bot(test_swarm_bot_3)

        test_swarm_bot_1.define_data_flow(sensor_id, [test_swarm_bot_1.get_id(), test_swarm_bot_3.get_id()])

        sensor_read_val = test_swarm_bot_1.read_from_sensor(sensor_id)

        start_time = time.time()
        while ((time.time() < start_time + 10) and (sensor_read_val not in test_swarm_bot_3.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))):
            pass

        self.assertIn(sensor_read_val, test_swarm_bot_1.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertNotIn(sensor_read_val, test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertIn(sensor_read_val, test_swarm_bot_3.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))

    def test_dead_end_path_will_return_a_dead_end_response_during_message_propagation(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()
        test_swarm_bot_4 = self.create_swarm_bot()

        sensor_id = 0
        test_swarm_bot_1.add_sensor(sensor_id)

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_4)
        test_swarm_bot_2.connect_to_swarm_bot(test_swarm_bot_3)

        test_swarm_bot_1.define_data_flow(sensor_id, [test_swarm_bot_1.get_id(), test_swarm_bot_3.get_id()])

        sensor_read_val = test_swarm_bot_1.read_from_sensor(sensor_id)

        start_time = time.time()
        while ((time.time() < start_time + 10) and (sensor_read_val not in test_swarm_bot_3.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))):
            pass

        self.assertIn(sensor_read_val, test_swarm_bot_1.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertNotIn(sensor_read_val, test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertIn(sensor_read_val, test_swarm_bot_3.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertNotIn(sensor_read_val, test_swarm_bot_4.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
