from swarm_bot.src.message_types import MessageTypes


class MessageWrapper(object):
    def __init__(self, msg_id, sender_id: int, target_bot_id: int, message_type: MessageTypes, message_payload: dict, propagation_flag):
        self.id = msg_id

        self.sender_id = sender_id
        self.target_bot_id = target_bot_id
        self.message_type = message_type
        self.message_payload = message_payload
        self.propagation_flag = propagation_flag

    def get_target_bot_id(self):
        return self.target_bot_id

    def get_message_type(self) -> MessageTypes:
        return self.message_type

    def get_message_payload(self) -> dict:
        return self.message_payload

    def get_sender_id(self) -> int:
        return self.sender_id

    def get_id(self):
        return self.id

    def set_sender_id(self, new_sender_id):
        self.sender_id = new_sender_id

    def set_target_id(self, new_target_bot_id):
        self.target_bot_id = new_target_bot_id

    def get_propagation_flag(self):
        return self.propagation_flag
