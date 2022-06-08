from swarm_bot.src.message_types import MessageTypes


class MessageFormat(object):
    def __init__(self, sender_id: int, target_bot_id: int, message_type: MessageTypes, message_payload: dict):
        self.sender_id = sender_id
        self.target_bot_id = target_bot_id
        self.message_type = message_type
        self.message_payload = message_payload

    def get_message_type(self) -> MessageTypes:
        return self.message_type

    def get_message_payload(self) -> dict:
        return self.message_payload

    def get_sender_id(self) -> int:
        return self.sender_id
