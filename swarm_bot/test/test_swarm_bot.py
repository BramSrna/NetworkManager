import logging
import unittest

from swarm_bot.test.swarm_bot_test_class import SwarmBotTestClass


class TestSwarmBot(SwarmBotTestClass):
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
