from swarm_bot.src.message_channel.message_channel import MessageChannel
from swarm_bot.src.message_wrapper.message_wrapper import MessageWrapper


class LocalMessageChannel(MessageChannel):
    def __init__(self, source_bot, target_bot):
        self.source_bot = source_bot
        self.target_bot = target_bot

    def send_message(self, message: MessageWrapper) -> None:
        self.target_bot.receive_message(message)
