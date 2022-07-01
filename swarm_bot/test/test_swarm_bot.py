import logging
import unittest
import time

from swarm_bot.src.swarm_bot import SwarmBot
from swarm_bot.test.swarm_bot_test_class import SwarmBotTestClass


class TestSwarmBot(SwarmBotTestClass):
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
