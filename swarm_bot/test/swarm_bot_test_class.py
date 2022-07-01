import unittest

from swarm_bot.src.swarm_bot import SwarmBot

class SwarmBotTestClass(unittest.TestCase):
    def setUp(self):
        self.test_swarm_bots = []

    def tearDown(self):
        for bot in self.test_swarm_bots:
            bot.teardown()

    def create_swarm_bot(self):
        new_bot = SwarmBot()
        self.test_swarm_bots.append(new_bot)
        return new_bot
