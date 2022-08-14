from swarm_bot.src.message_types import MessageTypes


class MessageWrapper(object):
    def __init__(self, msg_id, sender_id: int, target_bot_id: int, message_type: MessageTypes, message_payload: dict, sync_message):
        self.id = msg_id

        self.sender_id = sender_id
        self.propagator_id = sender_id
        self.target_bot_id = target_bot_id
        self.message_type = message_type
        self.message_payload = message_payload
        self.sync_message = sync_message

        self.intermediaries = [self.sender_id]

    def get_target_bot_id(self):
        return self.target_bot_id

    def get_message_type(self) -> MessageTypes:
        return self.message_type

    def get_message_payload(self) -> dict:
        return self.message_payload

    def get_original_sender_id(self) -> int:
        return self.sender_id

    def add_intermediary(self, bot_id):
        self.propagator_id = bot_id
        self.intermediaries.append(bot_id)

    def get_id(self):
        return self.id

    def get_intermediaries(self):
        return self.intermediaries

    def get_propagator_id(self):
        return self.propagator_id

    def is_sync_message(self):
        return self.sync_message
