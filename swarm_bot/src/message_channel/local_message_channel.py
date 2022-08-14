from swarm_bot.src.message_channel.message_channel import MessageChannel
from swarm_bot.src.message_wrapper.message_wrapper import MessageWrapper
from swarm_bot.src.swarm_bot import SwarmBot


class LocalMessageChannel(MessageChannel):
    def __init__(self, source_bot: SwarmBot, target_bot: SwarmBot):
        self.source_bot = source_bot
        self.target_bot = target_bot

    def send_message(self, message: MessageWrapper) -> None:
        self.target_bot.receive_message(message)
