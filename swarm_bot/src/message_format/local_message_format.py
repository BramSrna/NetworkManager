from swarm_bot.src.message_format.message_format import MessageFormat


class LocalMessageFormat(MessageFormat):
    def __init__(self, sender_id, target_bot_id, message_type, message_payload):
        self.sender_id = sender_id
        self.target_bot_id = target_bot_id
        self.message_type = message_type
        self.message_payload = message_payload

    def get_message_type(self):
        return self.message_type

    def get_message_payload(self):
        return self.message_payload

    def get_sender_id(self):
        return self.sender_id
