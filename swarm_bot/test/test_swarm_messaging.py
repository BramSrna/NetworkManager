import logging
import unittest

from swarm_bot_test_class import SwarmBotTestClass
from swarm_bot.src.swarm_bot_sensor import SwarmBotSensor
from swarm_bot.src.message_types import MessageTypes


class SimpleSensor(SwarmBotSensor):
    def __init__(self):
        super().__init__()

    def read_from_sensor(self, additional_params):
        return True


class TestSwarmMessaging(SwarmBotTestClass):
    def test_bot_will_receive_sent_message(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)

        msg_id = test_swarm_bot_1.create_message(test_swarm_bot_2.get_id(), MessageTypes.SENSOR_VAL, {"SENSOR_ID": 0, "DATA": 17})

        self.wait_for_idle_swarm()

        self.assertTrue(test_swarm_bot_1.sent_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_2.received_msg_with_id(msg_id))

    def test_swarm_bot_will_throw_error_when_data_flow_is_defined_with_unknown_bot_no_bots(self):
        test_swarm_bot_1 = self.create_swarm_bot()

        sensor = SimpleSensor()
        sensor_id = sensor.get_id()

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [15])

        self.assertIn("unknown sensor", str(raised_error.exception))

        test_swarm_bot_1.add_sensor(sensor)

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [15])

        self.assertIn("unknown swarm bot:", str(raised_error.exception))

    def test_swarm_bot_will_throw_error_when_data_flow_is_defined_with_unreachable_bot_through_intermediary(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)

        sensor = SimpleSensor()
        sensor_id = sensor.get_id()

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [-15])

        self.assertIn("unknown sensor", str(raised_error.exception))

        test_swarm_bot_1.add_sensor(sensor)

        with self.assertRaises(Exception) as raised_error:
            test_swarm_bot_1.define_data_flow(sensor_id, [-15])

        self.assertIn("unknown swarm bot:", str(raised_error.exception))

    def test_swarm_bot_will_follow_defined_data_flow_when_sensor_value_read(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()
        test_swarm_bot_3 = self.create_swarm_bot()

        sensor = SimpleSensor()
        sensor_id = sensor.get_id()
        test_swarm_bot_1.add_sensor(sensor)

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_3)

        test_swarm_bot_1.define_data_flow(sensor_id, [test_swarm_bot_1.get_id(), test_swarm_bot_2.get_id(), test_swarm_bot_3.get_id()])

        sensor_read_val = test_swarm_bot_1.read_from_sensor(sensor_id, ())

        self.wait_for_idle_swarm()

        self.assertIn(sensor_read_val, test_swarm_bot_1.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertIn(sensor_read_val, test_swarm_bot_2.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))
        self.assertIn(sensor_read_val, test_swarm_bot_3.read_from_memory(test_swarm_bot_1.get_id(), sensor_id))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
