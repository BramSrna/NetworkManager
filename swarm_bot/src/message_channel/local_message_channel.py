from swarm_bot.src.message_channel.message_channel import MessageChannel
from swarm_bot.src.message_format.message_format import MessageFormat
from swarm_bot.src.swarm_bot import SwarmBot


class LocalMessageChannel(MessageChannel):
    def __init__(self, source_bot: SwarmBot, target_bot: SwarmBot):
        self.source_bot = source_bot
        self.target_bot = target_bot

    def send_message(self, message: MessageFormat) -> None:
        self.target_bot.receive_message(message)
