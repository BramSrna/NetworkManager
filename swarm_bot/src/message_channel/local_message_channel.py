from swarm_bot.src.message_channel.message_channel import MessageChannel


class LocalMessageChannel(MessageChannel):
    def __init__(self, source_bot, target_bot):
        self.source_bot = source_bot
        self.target_bot = target_bot

    def send_message(self, message):
        self.target_bot.receive_message(message)
