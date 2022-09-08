import unittest

from swarm_bot.src.swarm_bot import SwarmBot
from swarm_bot.src.swarm_bot_idle_listener_interface import SwarmBotIdleListenerInterface


class SwarmBotTestClass(unittest.TestCase, SwarmBotIdleListenerInterface):
    def setUp(self):
        SwarmBotIdleListenerInterface.__init__(self)
        self.test_swarm_bots = []
        self.test_swarm_managers = []

    def tearDown(self):
        for swarm_manager in self.test_swarm_managers:
            swarm_manager.teardown()

        for bot in self.test_swarm_bots:
            bot.teardown()

    def create_swarm_bot(self):
        new_bot = SwarmBot()
        self.test_swarm_bots.append(new_bot)
        new_bot.add_idle_listener(self)
        return new_bot
