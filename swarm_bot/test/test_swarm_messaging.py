import logging
import unittest

from swarm_bot.test.swarm_bot_test_class import SwarmBotTestClass


class TestSwarmMessaging(SwarmBotTestClass):
    def test_bot_will_receive_sent_message(self):
        test_swarm_bot_1 = self.create_swarm_bot()
        test_swarm_bot_2 = self.create_swarm_bot()

        test_swarm_bot_1.connect_to_swarm_bot(test_swarm_bot_2)
        test_swarm_bot_2.connect_to_swarm_bot(test_swarm_bot_1)

        msg_id = test_swarm_bot_1.create_directed_message(test_swarm_bot_2.get_id(), "TEST", {})

        self.wait_for_idle_swarm()

        self.assertTrue(test_swarm_bot_1.sent_msg_with_id(msg_id))
        self.assertTrue(test_swarm_bot_2.received_msg_with_id(msg_id))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
