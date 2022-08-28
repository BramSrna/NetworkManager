from swarm_bot.src.message_wrapper.message_wrapper import MessageWrapper
from swarm_bot.src.message_types import MessageTypes


class LocalMessageWrapper(MessageWrapper):
    def __init__(self, msg_id, sender_id: int, target_bot_id: int, message_type: MessageTypes, message_payload: dict):
        super().__init__(msg_id, sender_id, target_bot_id, message_type, message_payload)
