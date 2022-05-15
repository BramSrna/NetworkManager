from common.src.message_types import MessageTypes


class HttpCommunicator(object):
    def __init__(self):
        pass

    def send_message(self, sender_id: str, receiver_id: str, message_type: MessageTypes, message_payload: dict) -> None:
        raise Exception("ERROR: The send_message method must be implemented by the child class.")

    def receive_message(self, sender_id: str, message_type: MessageTypes, message_payload: dict) -> None:
        raise Exception("ERROR: The receive_message method must be implemented by the child class.")

    def get_id(self) -> None:
        raise Exception("ERROR: The get_id method must be implemented by the child class.")

