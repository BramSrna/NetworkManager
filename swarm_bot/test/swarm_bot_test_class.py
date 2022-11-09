import unittest

from swarm_bot.src.swarm_bot import SwarmBot
from swarm_bot.src.swarm_bot_idle_listener_interface import SwarmBotIdleListenerInterface


class SwarmBotTestClass(unittest.TestCase, SwarmBotIdleListenerInterface):
    def setUp(self):
        SwarmBotIdleListenerInterface.__init__(self)
        self.test_swarm_bots = []

    def tearDown(self):
        for bot in self.test_swarm_bots:
            bot.teardown()

    def create_swarm_bot(self, additional_config_dict={}):
        new_bot = SwarmBot(additional_config_dict=additional_config_dict)
        self.test_swarm_bots.append(new_bot)
        new_bot.add_idle_listener(self)
        return new_bot
