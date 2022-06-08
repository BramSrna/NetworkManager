from swarm_bot.src.message_format.message_format import MessageFormat
from swarm_bot.src.message_types import MessageTypes


class LocalMessageFormat(MessageFormat):
    def __init__(self, sender_id: int, target_bot_id: int, message_type: MessageTypes, message_payload: dict):
        super().__init__(sender_id, target_bot_id, message_type, message_payload)
